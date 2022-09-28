# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SuscriptionProcess(models.Model):
    _name = 'subscription.process'
    _inherit = 'mail.thread'
    _description = 'Process'

    name = fields.Char(
        string="Name")
    active = fields.Boolean(
        string="Active",
        default=True)


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
