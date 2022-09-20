# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskCategUdn(models.Model):
    _name = 'project.task.categ.udn'
    _inherit = 'mail.thread'
    _description = 'Category Udn OT'

    name = fields.Char(
        string="Name",
        tracking=True)
    code = fields.Char(
        string="Code",
        tracking=True)
    description = fields.Char(
        string="Description",
        tracking=True)
    ot_type_id = fields.Many2one(
        'project.task.ot.type',
        string="OT type")
    

    @api.onchange('name','code')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
        self.code = self.code.upper() if self.code else False
