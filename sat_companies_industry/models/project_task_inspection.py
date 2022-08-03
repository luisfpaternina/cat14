# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskInspection(models.Model):
    _name = 'project.task.inspection'
    _inherit = 'mail.thread'
    _description = 'Inspections'

    name = fields.Char(
        string="Periodicity",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        tracking=True,
        default=True)
    description = fields.Text(
        string="Description",
        tracking=True)

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
