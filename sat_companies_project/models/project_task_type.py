# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_project_fsm = fields.Boolean(
        string="Is done in fsm project")
    is_progress = fields.Boolean(
        string="Progress stage")
    is_send_to_supervisor = fields.Boolean(
        string="Send to supervisor")
