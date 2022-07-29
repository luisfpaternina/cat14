# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrEmployeeCategory(models.Model):
    _name = 'hr.employee.categories'
    _inherit = 'mail.thread'
    _description = 'Employee category'

    name = fields.Char(
        string="Employee's category",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        default=True)
