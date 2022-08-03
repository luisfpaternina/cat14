# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BimCostList(models.Model):
    _description = "Bim Cost List"
    _name = 'bim.cost.list'
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Name', required=True)
    partner_id = fields.Many2one('res.partner')
    state_id = fields.Many2one('res.country.state')
    line_ids = fields.One2many('bim.cost.list.line', 'cost_id')

    def _get_product_bim_cost_list(self,product_id):
        cost_line_ids = self.env['bim.cost.list.line'].search([('product_id','=',product_id.id),('cost_id','=',self.id)])
        product_cost = False
        for line in cost_line_ids:
            product_cost = line.price
            break
        return product_cost


class BimCostListline(models.Model):
    _name = 'bim.cost.list.line'
    _description = 'Bim Cost List Line'
    _order = 'sequence'

    cost_id = fields.Many2one('bim.cost.list')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('product.product', required=True)
    price = fields.Float(required=True)




