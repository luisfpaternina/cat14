# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_potential_client = fields.Boolean(
        string="Is a potential client",
        related="partner_id.is_potential_client")


    @api.constrains('partner_id','account_id')
    def _is_validate_potencial_client(self):
        for record in self:
            if record.is_potential_client:
                raise ValidationError(_('Validate potencial client'))
