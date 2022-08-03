# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockGadgetsTypesAsistance(models.Model):
    _name = 'stock.gadgets.types.assistance'
    _inherit = 'mail.thread'
    _description = 'Gadgets types asistance'

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