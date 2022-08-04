# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockProductTags(models.Model):
    _name = 'stock.product.tags'
    _inherit = 'mail.thread'
    _description = 'Product tags'

    name = fields.Char(
        string="Name",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        tracking=True,
        default=True)
    color = fields.Integer(
        string="Color")

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False