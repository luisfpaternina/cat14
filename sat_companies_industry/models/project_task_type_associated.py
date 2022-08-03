# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskTypeAssociated(models.Model):
    _name = 'project.task.type.associated'
    _inherit = 'mail.thread'
    _description = 'Types of associated tasks'

    name = fields.Char(
        string="Name",
        tracking=True)
    code = fields.Char(
        string="Code",
        tracking=True)
    description = fields.Char(
        string="Description",
        tracking=True)
    type_ot = fields.Char(
        string="Type OT",
        tracking=True)


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False