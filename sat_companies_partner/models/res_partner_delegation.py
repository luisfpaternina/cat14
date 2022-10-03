# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartnerDelegation(models.Model):
    _name = 'res.partner.delegation'
    _inherit = 'mail.thread'
    _description = 'Delegations'
    _rec_name = 'code'

    name = fields.Char(
        string="Name",
        tracking=True)
    code = fields.Char(
        string="Postal Code",
        tracking=True)
    country_id = fields.Many2one(
        'res.country',
        string="Country",
        tracking=True)

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
