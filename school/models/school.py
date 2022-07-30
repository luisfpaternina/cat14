# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class School(models.Model):

    _name = "school"
    _inherit = 'mail.thread'
    _description = "School"

    name = fields.Char(string='Name', required=True, tracking=True)
    identification_type = fields.Selection([('cc','CC'),('ni','NI'),('ce','CE')], string="Identification Type", tracking=True)
    identification_number = fields.Char(string="Identification number", tracking=True)
    photo = fields.Binary(string='Photo', tracking=True)
    dob = fields.Date(string="Date of Birth", tracking=True)
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], string='Gender')
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        string='Blood Group')
    nationality = fields.Many2one('res.country', string='Nacionality')
    city_id = fields.Many2one('res.city', string="City")
    attachment = fields.Binary(string="Attachment", tracking=True)
 