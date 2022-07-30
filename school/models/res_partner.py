# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import re
from datetime import date


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean(
        string="Is student")

    def compute_is_student(self):
        student_obj = self.env['students'].search([('name', '=', self.name)], limit=1)
        if student_obj:
            self.is_student = True
        else:
            self.is_student = False
