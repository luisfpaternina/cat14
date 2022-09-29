# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderTemplateInherit(models.Model):
    _inherit = 'sale.order'
    
    gadgets_contract_type_id = fields.Many2one('stock.gadgets.contract.type')

    @api.onchange('sale_type_id','gadgets_contract_type_id')
    def sale_order_template_domain(self):
        for record in self:
            record.sale_order_template_id = False
            if record.sale_type_id and record.type_contract:
                sales_orders = self.env['sale.order.template'].search([('sale_type_id','=', record.sale_type_id.id),('gadgets_contract_type_id','=', record.gadgets_contract_type_id.id)])
                ids_order_templates = sales_orders.ids
        
                return {'domain': {'sale_order_template_id': [('id', 'in', ids_order_templates)]}}
            else:
                sales_orders = self.env['sale.order.template'].search([('sale_type_id','=', False),('type_contract','=', False)])
                ids_order_templates = sales_orders.ids
        
                return {'domain': {'sale_order_template_id': [('id', 'in', ids_order_templates)]}}