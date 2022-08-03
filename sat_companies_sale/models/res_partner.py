# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_admin = fields.Boolean(
        string="Is Admin",
        tracking=True)
    is_low = fields.Boolean(
        string="Is low")
   