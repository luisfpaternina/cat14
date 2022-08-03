# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleCheckTypeContract(models.Model):
    _name = 'sale.check.type.contract'

    name = fields.Char()
    item = fields.Integer(
        store=True)
    type_service_id = fields.Many2one(
        'sale.type.service',
        'Type Service')
    check_service = fields.Boolean(
        'Check Service in contract')
    order_id = fields.Many2one(
        'sale.order',
        string="Sale Order")
