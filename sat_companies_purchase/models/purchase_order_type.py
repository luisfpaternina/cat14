# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class   PurchaseOrderType(models.Model):
    _name = 'purchase.order.type'
    _inherit = 'mail.thread'
    _description = 'Purchase order type'

    name = fields.Char(
        string="Name",
        tracking=True)
    active = fields.Boolean(
        string="Active")


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
