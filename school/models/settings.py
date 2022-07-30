# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class Settings(models.Model):

    _name = "settings"
    _inherit = 'mail.thread'
    _description = "Settings"

    
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True)

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
   