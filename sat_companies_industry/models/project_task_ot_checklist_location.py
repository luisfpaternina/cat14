# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskOtChecklistLocation(models.Model):
    _name = 'project.task.ot.checklist.location'
    _inherit = 'mail.thread'
    _description = 'OT checklist location'

    name = fields.Char(
        string="Name",
        tracking=True)


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
