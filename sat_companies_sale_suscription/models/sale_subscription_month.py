# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleSuscriptionMonth(models.Model):
    _name = 'sale.subscription.month'

    name = fields.Char('Name')
    active = fields.Boolean(default=True)
    code = fields.Integer('Code')
    sale_subscription_id = fields.Many2one('sale.subscription')
