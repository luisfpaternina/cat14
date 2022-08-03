# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleSubscriptionTemplate(models.Model):
    _inherit = 'sale.subscription.template'

    is_maintenance = fields.Boolean(
        string="Is a maintenance",
        tracking=True)
