# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import exceptions

class sale_order(models.Model):    
       
    _inherit  = 'sale.order'
                                 
    x_lost_reason_id = fields.Many2one('crm.lost.reason', string="Reason lost", copy=False,track_visibility='onchange');
       

    def do_reject_quotation(self):
        view_id = self.env.ref('oi1_sale_quotrejection.sale_order_lost_view_form');
        return {
                'name': _('Cancel Quotation'),
                'view_mode': 'form',
                'view_id': view_id.id,
                'view_type': 'form',
                'res_model': 'sale_order_lost_wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                
        }
