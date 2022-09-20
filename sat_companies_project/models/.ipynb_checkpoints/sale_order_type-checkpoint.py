# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderType(models.Model):
    _name = 'sale.order.type'
    _inherit = 'mail.thread'
    _description = 'Sale order type'

    name = fields.Char(
        string="Name",
        tracking=True)
    code = fields.Char(
        string="Code",
        tracking=True)
    active  = fields.Boolean(
        string="Active",
        tracking=True,
        default=True)
    is_create_task = fields.Boolean(
        string="Create task",
        tracking=True)
    project_stage_ids = fields.Many2many(
        'project.task.type',
        string="Stages",
        tracking=True)
    project_task_ids = fields.Many2many(
        'project.task',
        string="Tasks",
        tracking=True)


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
