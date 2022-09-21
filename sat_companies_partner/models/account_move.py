# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_potential_client = fields.Boolean(
        string="Is a potential client")
    is_validate = fields.Boolean(
        string="Validate")
    has_account = fields.Boolean(
        string="Has a account",
        related="partner_id.has_account")
    client_code = fields.Char(
        string="Client code",
        related="partner_id.client_code")


    def action_post(self):
        for record in self:
            if record.is_potential_client:
                raise ValidationError(_(
                    'Validate potencial client!'))
        return super(AccountMove, self).action_post()
