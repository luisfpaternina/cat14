import calendar
from odoo.tools import formatLang
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _


class LicencePlatesWizard(models.TransientModel):
    _name = "license.plates.wizard"
    _description = "Licence plates wizard"

    student_id = fields.Many2one(
        'students',
        string="Student")
    license_plates_id = fields.Many2one(
        'license.plates',
        string="Licence plates")
    description = fields.Text(
        string="Description")
    

    def cancel_licence_plates(self):
        license_plates_obj =  self.env['license.plates'].search([('id','=',self.license_plates_id.id)])
        if license_plates_obj:
            license_plates_obj.write({
                'description': self.description, 
                'student_id': self.student_id.id
                })
