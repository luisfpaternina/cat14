# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SuscriptionInspectionReport(models.Model):
    _name = 'subscription.inspection.report'
    _inherit = 'mail.thread'
    _description = 'Inspection report'

    name = fields.Char(
        string="Name")
    active = fields.Boolean(
        string="Active",
        default=True)


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
