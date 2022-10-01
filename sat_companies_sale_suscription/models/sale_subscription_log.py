# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderTemplateInherit(models.Model):
    _inherit = 'sale.subscription.log'

    project_task_id = fields.Many2one(
        'project.task')
