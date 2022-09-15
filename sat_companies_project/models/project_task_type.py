# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_project_fsm = fields.Boolean(
        string="Is done in fsm project")
    

    _sql_constraints = [
        (
            'is_project_fsm_uniq',
            'unique (is_project_fsm)',
            'Only one stage can be marked as done in external service')
    ]
