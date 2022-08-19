# -*- coding: utf-8 -*-
##################################################################################################################################
#
# ING.LUIS FELIPE PATERNINA VITAL
#  
# Correo: lfpaternina93@gmail.com
#
#
# Celular: +573046079971 or +573215062353
#
# Bogotá,Colombia
#
###################################################################################################################################
from odoo import models, fields, api, _
from odoo.addons.mail.models import mail_template


class LicensePlates(models.Model):

    _name = "license.plates"
    _inherit = 'mail.thread'
    _description = "License plates"

    name = fields.Char(
        string="Nombre",
        readonly=True,
        required=True,
        copy=False,
        tracking=True,
        default='New')
    student_id = fields.Many2one(
        'students',
        string="Student")
    course = fields.Char(
        string="Course")
    create_date = fields.Datetime(
        'Create Date',
        tracking=True,
        default= fields.Datetime().now())
    identification_number = fields.Char(
        string="Identification number",
        tracking=True,
        related="student_id.identification_number")
    blood_group = fields.Selection(
        string="Blood Group",
        related="student_id.blood_group")
    identification_type = fields.Selection(
        string="Identification Type",
        related="student_id.identification_type")
    address = fields.Char(
        string="Address",
        related="student_id.address")
    cellphone = fields.Char(
        string="Phone",
        related="student_id.cellphone")
    neighborhood = fields.Char(
        string="Neighborhood",
        related="student_id.neighborhood")
    gender = fields.Selection(
        string="Gender",
        related="student_id.gender")
    email = fields.Char(
        string="Email",
        related="student_id.email")
    course_line_ids = fields.One2many(
        'license.plates.lines',
        'license_plates_id',
        string="Courses")
    notes = fields.Html(
        string="Notes")
    description = fields.Text(
        string="Description")
    state = fields.Selection([
        ('draft','Draft'),
        ('finished','Finished')],string="State", default="draft")

    def action_show_wizard(self):
       return {'type': 'ir.actions.act_window',
               'name': _('Cancel licence plates'),
               'res_model': 'license.plates.wizard',
               'target': 'new',
               'view_id': self.env.ref('school.license_plates_wizard_form').id,
               'view_mode': 'form',
               'context': {}
               }


    def method_name(self):
        converted_content = mail_template.mako_template_env.from_string(notes).render({'object': object_value,})
        return converted_content


    #Secuencia para las matriculas de los estudiantes
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('license.plates') or 'New'

        result = super(LicensePlates, self).create(vals)
        return result


    #crear nuevo registro en sale.order
    def create_record_in_Sale_order(self):

        vals = {

           'name': self.name,
           'partner_id': self.student_id.id,
           'validity_date': self.create_date,
           
		}
        self.env['sale.order'].create(vals)


    @api.onchange('student_id')
    def get_records(self):
        for rec in self:
            lines = []
            student_obj = rec.env['students'].search([('id', '=', rec.student_id.id)],limit=1)
            if student_obj:
                for s in student_obj.course_line_ids:
                    vals = (0, 0, {
                        'course_id': s.course_id.id,
                    })
                    lines.append(vals)
                rec.course_line_ids = lines

    


class LicensePlatesLines(models.Model):

    _name = "license.plates.lines"
    _description = "License plates lines"

    course_id = fields.Many2one(
        'courses',
        string="Course")
    student_id = fields.Many2one(
        'students',
        string="Student")
    license_plates_id = fields.Many2one(
        'license.plates',
        string="License plates")
