# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Students(models.Model):

    _name = "students"
    _inherit = 'mail.thread'
    _description = "students"

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True)
    identification_type = fields.Selection([
        ('cc','CC'),
        ('ni','NI'),
        ('ce','CE')], string="ID Type", tracking=True)
    identification_number = fields.Char(
        string="Identification Number",
        tracking=True)
    photo = fields.Binary(
        string='Photo',
        tracking=True)
    dob = fields.Date(
        string="Date of Birth",
        tracking=True)
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Otro')], string='Gender')
    blood_group = fields.Selection(
        [('A+', 'A+'), ('B+', 'B+'), ('O+', 'O+'), ('AB+', 'AB+'),
         ('A-', 'A-'), ('B-', 'B-'), ('O-', 'O-'), ('AB-', 'AB-')],
        string='Blood Group')
    nationality = fields.Many2one(
        'res.country',
        string='Nacionality')
    city_id = fields.Many2one(
        'res.city',
        string="City")
    attachment = fields.Binary(
        string="Attachment",
        tracking=True)
    address = fields.Char(
        string="Address")
    cellphone = fields.Char(
        string="Phone")
    neighborhood = fields.Char(
        string="Neighborhood")
    email = fields.Char(
        string="Email")
    course_line_ids = fields.One2many(
        'students.lines',
        'student_id',
        string="Courses")
    student_count = fields.Integer(
        string="student count",
        compute="compute_teacher_count")
    hobby_id = fields.Many2many(
        'hobbies',
        string="Hobby")
    is_student = fields.Boolean(
        string="Is student",
        compute="create_student_partner")


    def get_license_plates(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Licences',
            'view_mode': 'tree',
            'res_model': 'license.plates',
            'domain': [('student_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_teacher_count(self):
        for record in self:
            record.student_count = self.env['license.plates'].search_count([('student_id', '=', self.id)])


    _sql_constraints = [

    ('name_unique',
     'UNIQUE(identification_number)',
     "The identification number must be unique!")

    ]

    @api.onchange('name')
    def _upper_name(self):
    # Colocar mayusculas de forma automatica       
        self.name = self.name.upper() if self.name else False

    def create_student_partner(self):
    # Crear un contacto res.partner
        for record in self:
            partner = record.env['res.partner'].create({
                'name': record.name
                })
            record.is_student = True

    @api.model
    def create(self, vals):
    # Heredar la función create para crear un contacto desde estudiantes
      self.create_student_partner()
      return super(Students, self).create(vals)



class StudentsLines(models.Model):

    _name = "students.lines"
    _description = "students lines"

    course_id = fields.Many2one(
        'courses',
        string="Course")
    student_id = fields.Many2one(
        'students',
        string="Student")
  