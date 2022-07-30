# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class Hobbies(models.Model):

    _name = "hobbies"
    _inherit = 'mail.thread'
    _description = "Hobbies"

    
    name = fields.Char(string='Name', required=True, tracking=True)
    color = fields.Integer(string="Color")

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
   