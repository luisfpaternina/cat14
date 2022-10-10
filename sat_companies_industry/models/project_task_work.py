# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskWork(models.Model):
    _name = 'project.task.work'
    _inherit = 'mail.thread'
    _description = 'Works'

    name = fields.Text(
        string="Description",
        tracking=True)
    is_done = fields.Boolean(
        string="Is done")
    task_id = fields.Many2one(
        'project.task',
        string="Task")
