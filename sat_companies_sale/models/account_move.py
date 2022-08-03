# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging


class AccountMove(models.Model):
    _inherit = 'account.move'

    gadgets_contract_type_id = fields.Many2one(
        'stock.gadgets.contract.type')
    suscription_id = fields.Many2one(
        'sale.subscription',
        string="Subscription")
