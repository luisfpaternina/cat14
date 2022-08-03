# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
from io import BytesIO


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_potential_client = fields.Boolean(
        string="Is a potential client",
        tracking=True)
    payment_term_maintenance_id = fields.Many2one(
        'account.payment.term',
        string="Terms maintenance sale")
    payment_term_tel_id = fields.Many2one(
        'account.payment.term',
        string="Terms telephone sale")


    @api.onchange('company_type')
    def _validate_company_type(self):
        for record in self:
            if record.company_type == 'company':
                record.is_potential_client = True
            else:
                record.is_potential_client = False
