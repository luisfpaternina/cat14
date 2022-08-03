# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskOtType(models.Model):
    _name = 'project.task.ot.type'
    _inherit = 'mail.thread'
    _description = 'OT type'
    _rec_name = 'code'

    code = fields.Char(
        string="Code",
        tracking=True)
    ot_type = fields.Char(
        string="Type",
        tracking=True)
    description = fields.Text(
        "Description",
        tracking=True)


    @api.onchange('code','ot_type','description')
    def _upper_fields(self):        
        self.code = self.code.upper() if self.code else False
        self.ot_type = self.ot_type.upper() if self.ot_type else False
        self.description = self.description.upper() if self.description else False
