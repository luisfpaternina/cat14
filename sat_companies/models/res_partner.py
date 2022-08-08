# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_potential_client = fields.Boolean(
        string="Is a potential client",
        tracking=True,
        default=True)
    is_admin = fields.Boolean(
        string="Is Admin",
        tracking=True)
    is_maintainer = fields.Boolean(
        string="Is maintainer",
        tracking=True)
    is_oca = fields.Boolean(
        string="O.C.A",
        tracking=True)
    is_acommunity = fields.Boolean(
        string="Is a community")
    is_billing_administrator = fields.Boolean(
        string="Is billing administrator")
    potencial_contact = fields.Boolean(
        string="Validator potencial contact")


    @api.constrains(
        'name',
        'bank_ids',
        'vat',
        'city',
        'street',
        'is_potential_client',
        'is_maintainer',
        'is_oca',
        'is_admin')
    def validate_fields(self):
        for record in self:
            potencial_contact = self.env['ir.config_parameter'].sudo().get_param('sat_companies.is_potencial_client') or False
            record.potencial_contact = potencial_contact
            if record.potencial_contact:
                if not record.is_admin and not record.is_maintainer\
                    and not record.is_oca and not record.is_potential_client:
                        if not record.vat:
                            raise ValidationError(_(
                                'You must register an identification number'))
                        if not record.bank_ids:
                            raise ValidationError(_(
                                'You must register a Bank account'))
                        if not record.city:
                            raise ValidationError(_(
                                'You must register a city'))
