# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _inherit = 'mail.thread'
    _description = 'Partner type'

    name = fields.Char(
        string="Partner's type",
        tracking=True)
    code = fields.Char(
        string="Code",
        tracking=True)
    is_community = fields.Boolean(
        string="Is community")
    is_maker = fields.Boolean(
        string="Is maker")


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
