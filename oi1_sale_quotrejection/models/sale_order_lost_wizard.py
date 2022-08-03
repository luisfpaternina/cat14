# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CrmLeadLost(models.TransientModel):
    _name = 'sale_order_lost_wizard'
    _description = 'Cancel Quotation'

    lost_reason_id          = fields.Many2one('crm.lost.reason', 'Lost Reason')
    create_new_quotation    = fields.Boolean(string='Create new Quotation', default=False);

    def action_lost_reason_apply(self):
        sale_orders = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        sale_orders.write({'x_lost_reason_id': self.lost_reason_id.id,'state':'cancel'})        
        if self.create_new_quotation == True: 
            for sale_order in sale_orders: 
                sale_order_new = sale_order.copy();
                sale_order_new.origin = sale_order.name; 
