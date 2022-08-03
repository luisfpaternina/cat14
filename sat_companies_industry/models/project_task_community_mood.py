# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TaskCommunityMood(models.Model):
    _name = 'task.community.mood'
    _inherit = 'mail.thread'
    _description = 'Inspections'

    name = fields.Char(
        string="Name",
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
