# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    origin_po = fields.Char(
        string="Origen")
    is_payment_validator = fields.Boolean(
        string="Payment validate")
