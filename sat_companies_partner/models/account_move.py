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


    @api.constrains('name', 'partner_id')
    def _validate_has_account(self):
        for record in self:
            if record.has_account:
                raise ValidationError(_(
                    'Validate potencial client has account!'))


    def write(self, values):
        for record in self:
            if record.has_account:
                raise ValidationError(_(
                    'Validate potencial client has account!'))
        return super(AccountMove, self).write(values)


    def action_post(self):
        for record in self:
            if record.is_potential_client:
                raise ValidationError(_(
                    'Validate potencial client!'))
        return super(AccountMove, self).action_post()
