# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskTemplate(models.Model):
    _name = 'project.task.template'
    _inherit = 'mail.thread'
    _description = 'Task templates'

    name = fields.Char(
        string="Name",
        tracking=True)
    task_ids = fields.Many2many(
        'project.task',
        string="Tasks")
    active = fields.Boolean(
        string="Active",
        tracking=True,
        default=True)


    @api.onchange('name')
    def _upper_name(self):
    # COLOCAR CAMPO NAME EN MAYUSCULAS     
        self.name = self.name.upper() if self.name else False
