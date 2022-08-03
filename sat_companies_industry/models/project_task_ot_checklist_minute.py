# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import datetime
import logging


class ProjectTaskOtChecklistMinute(models.Model):
    _name = 'project.task.checklist.minute'
    _inherit = 'mail.thread'
    _description = 'OT checklist minute'

    name = fields.Char(
        string="Name",
        tracking=True)
    task_id = fields.Many2one(
        'project.task',
        string="Task",
        tracking=True)
    minute_point_id = fields.Many2one(
        'maintenance.minute.point',
        string="Minute point",
        tracking=True)
    type_deffect_id = fields.Many2one(
        'maintenance.type.deffect',
        string="Type of deffect",
        tracking=True,
        related="minute_point_id.type_deffect_id")
    is_reviewed = fields.Boolean(
        string="Is reviewed")
    minute_point_description = fields.Text(
        string="Description",
        related="minute_point_id.description")
