# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountMoveUnpaid(models.Model):
    _name = 'account.move.unpaid'
    _inherit = 'mail.thread'
    _description = 'Unpaid'

    name = fields.Char(
        string="Name",
        tracking=True)
    date = fields.Date(
        string="Date",
        tracking=True)
