# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class Teachers(models.Model):

    _name = "teachers"
    _inherit = 'mail.thread'
    _description = "Teachers"

    name = fields.Char(string='Name', required=True, tracking=True)
    identification_type = fields.Selection([('cc','CC'),('ni','TI'),('ce','Passport')], string="Identification type", tracking=True)
    identification_number = fields.Char(string="Identification number", tracking=True)
    photo = fields.Binary(string='Photo', tracking=True)
    dob = fields.Date(string="Date of birth", tracking=True)
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], string='Gender')
    blood_group = fields.Selection(
        [('A+', 'A+'), ('B+', 'B+'), ('O+', 'O+'), ('AB+', 'AB+'),
         ('A-', 'A-'), ('B-', 'B-'), ('O-', 'O-'), ('AB-', 'AB-')],
        string='Blood Group')
    nationality = fields.Many2one('res.country', string='Nacionality',store=True)
    city_id = fields.Many2one('res.city', string="City", store=True)
    attachment = fields.Binary(string="CV", tracking=True)
    address = fields.Char(string="Address")
    phone = fields.Char(string="Phone")
    work_experience_ids = fields.One2many('work.experience', 'teacher_id', string="Work experience",tracking=True)
    applied_studies_ids = fields.One2many('applied.studies', 'teacher_id', string="Applied studies",tracking=True)
    civil_state = fields.Selection([
        ('single','Single'),
        ('married','Married'),
        ('ul','Free union'),
        ('vu','Widower'),
        ('sep','Divorced'),
        ('other','Other')],string="Civil state")
    teacher_count = fields.Integer(
        string="Teacher count",
        compute="compute_teacher_count")


    def get_courses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Courses',
            'view_mode': 'tree',
            'res_model': 'courses',
            'domain': [('teacher_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_teacher_count(self):
        for record in self:
            record.teacher_count = self.env['courses'].search_count([('teacher_id', '=', self.id)])

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
