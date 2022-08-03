# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockGadgetsIncreaseType(models.Model):
    _name = 'stock.gadgets.increase.type'
    _inherit = 'mail.thread'
    _description = 'Increase type'
    _rec_name = 'code'

    name = fields.Char(
        string="Name",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        tracking=True,
        default=True)
    code = fields.Char(
        string="Code",
        tracking=True)

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False