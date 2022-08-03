# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
from io import BytesIO


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_potential_client = fields.Boolean(
        string="Is a potential client",
        tracking=True,
        related="partner_id.is_potential_client")


    @api.constrains('partner_id')
    def _validate_is_potential_client(self):
        for record in self:
            if record.is_potential_client:
                raise ValidationError(_(
                    'Validate potential client in partner'))
