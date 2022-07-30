# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class Notes(models.Model):

    _name = "notes"
    _inherit = 'mail.thread'
    _description = "Notes"

    name = fields.Char(string='Name', required=True, tracking=True)

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
