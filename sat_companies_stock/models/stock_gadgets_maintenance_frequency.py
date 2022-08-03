# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockMaintenanceFrequency(models.Model):
    _name = 'stock.maintenance.frequency'
    _inherit = 'mail.thread'
    _description = 'Maintenance frequency'
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
