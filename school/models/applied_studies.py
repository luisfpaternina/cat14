# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class AppliedStudies(models.Model):

    _name = "applied.studies"
    _inherit = 'mail.thread'
    _description = "Applied studies"

    name = fields.Char(string='Tittle', required=True, tracking=True)
    status = fields.Selection([('done','Done'),('apl','Postponed'),('current','Current')],string="State", tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    teacher_id = fields.Many2one('teachers')
    institution = fields.Char(string="Institution", tracking=True)
  