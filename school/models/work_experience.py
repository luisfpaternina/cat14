# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class WorkExperience(models.Model):

    _name = "work.experience"
    _inherit = 'mail.thread'
    _description = "Experience"

    name = fields.Char(string='Tittle', required=True, tracking=True)
    status = fields.Selection([('done','Done'),('apl','Postponed'),('current','Current')],string="State", tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    teacher_id = fields.Many2one('teachers')
    institution = fields.Char(string="Institution", tracking=True)

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
  