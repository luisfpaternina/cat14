# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskWarning(models.Model):
    _name = 'project.task.warning'
    _inherit = 'mail.thread'
    _description = 'Warning'

    name = fields.Char(
        string="Name",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        default=True)
    

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False 
