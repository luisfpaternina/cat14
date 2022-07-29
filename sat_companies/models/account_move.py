# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
import qrcode


class AccountMove(models.Model):
    _inherit = 'account.move'

    move_unpaid_ids = fields.Many2many(
        'account.move.unpaid',
        string="Unpaids",
        tracking=True)
    qr_image = fields.Binary(
        "QR Code")
    qr_in_report = fields.Boolean(
        'Show QR in Report')
    invoice_qr_code = fields.Char(
        'QR Code')
    qr_code = fields.Binary(
        'QR Code Image')
    qr_code_name = fields.Char(
        default="qr_code.png")
    is_potential_client = fields.Boolean(
        string="Is a potential client",
        tracking=True)
    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Payment Status", store=True, readonly=False, copy=False, tracking=True)
