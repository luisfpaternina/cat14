# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrEmployeeType(models.Model):
    _name = 'hr.employee.type'
    _inherit = 'mail.thread'
    _description = 'Employee type'

    name = fields.Char(
        string="Employee's type",
        tracking=True)
    code = fields.Char(
        string="Code",
        tracking=True)
