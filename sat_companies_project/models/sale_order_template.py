# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderTemplateInherit(models.Model):
    _inherit = 'sale.order.template'

    sale_type_id = fields.Many2one(
        'sale.order.type',
        string="Sale type")
