# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class BimPriceMassiveWzd(models.TransientModel):
    _name = 'bim.price.massive.wzd'
    _description = 'bim.price.massive.wzd'

    def _get_default_budget(self):
        active_id = self._context.get('active_id')
        budget = self.env['bim.budget'].browse(active_id)
        return budget

    budget_id = fields.Many2one('bim.budget', string='Budget', default=_get_default_budget)
    product_id = fields.Many2one('product.template', string='Resource')
    pricelist_id = fields.Many2one('product.pricelist', string='Price List')
    new_price = fields.Float('Price New')
    type_update = fields.Selection([('cost', 'Update massive concepts according to current cost'),
                                    ('sale', 'Update massive concepts according to current price'),
                                    ('manual', 'Update bulk concepts manually'),
                                    ('agreed', 'Update massive concepts according to agreed prices'),
                                    ('pricelist', 'Update massive concepts according to pricelist')
                                    ], string="Type",  default='cost')
    type_price = fields.Selection([('price','Price'),('percent','Percent')], string="Type Price", default='price')
    duplicate = fields.Boolean(string="Duplicate Budget", default=False)

    def update_price(self):
        if self.duplicate:
           budget_id = self.budget_id.copy()
        else:
            budget_id = self.budget_id
        if self.type_update == 'cost':
            resources = budget_id.concept_ids.filtered(lambda self: self.type in ['material', 'labor', 'equip'])
            for resource in resources:
                resource.amount_fixed = resource.product_id.standard_price

        elif self.type_update == 'sale':
            resources = budget_id.concept_ids.filtered(lambda self: self.type in ['material', 'labor', 'equip'])
            for resource in resources:
                resource.amount_fixed = resource.product_id.lst_price

        elif self.type_update == 'agreed':
            project = budget_id.project_id
            if not project.price_agreed_ids:
                raise ValidationError(_('No existen registros de Productos con precios acordados para la Obra'))
            for line in project.price_agreed_ids:
                resources = budget_id.concept_ids.filtered(lambda x: x.product_id == line.product_id)
                for resource in resources:
                    resource.amount_fixed = line.price_agreed
        elif self.type_update == 'manual':
            concepts = self.env['bim.concepts'].search(
                [('budget_id', '=', budget_id.id), ('product_id', '=', self.product_id.id)])
            if self.new_price > 0.0:
                if self.type_price == 'price':
                    for concept in concepts:
                        concept.write({'amount_fixed': self.new_price})
                elif self.type_price == 'percent':
                    for concept in concepts:
                        concept.write({'amount_fixed': concept.amount_fixed * (self.new_price/100)})
            else:
                raise ValidationError(_('Price should be bigger than 0.0'))
        else:
            resources = budget_id.concept_ids.filtered(lambda self: self.type in ['material', 'labor', 'equip'])
            for resource in resources:
                if self.pricelist_id:
                    resource.amount_fixed = self.pricelist_id.get_product_price(resource.product_id, resource.quantity,
                                                                                budget_id.project_id.customer_id,
                                                                                False, False)
