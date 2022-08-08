# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_down_payment = fields.Boolean(
        string="Is down payment")
    
    _sql_constraints = [
        ('down_payment', 'unique (is_down_payment)', 'Down payment is already exists...!')
    ]
