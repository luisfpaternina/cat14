# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class Courses(models.Model):

    _name = "courses"
    _inherit = 'mail.thread'
    _description = "Courses"

    
    name = fields.Char(
        string='Name of the subject',
        required=True,
        tracking=True)
    credit_number = fields.Integer(
        string="Credit Numbers")
    teacher_id = fields.Many2one(
        'teachers',
        string="Teacher in charge")
    area_ids = fields.Many2many(
        'area',
        string="Related areas")
    student_id = fields.Many2one(
        'students',
        string="Student")

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
  