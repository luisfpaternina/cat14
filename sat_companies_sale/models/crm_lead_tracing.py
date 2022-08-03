# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CrmLeadTracing(models.Model):
    _name = 'crm.lead.tracing'
    _inherit = 'mail.thread'
    _description = 'Tracing'

    name = fields.Char(
        string="Name")
    date = fields.Date(
        string="Date")
    description = fields.Text(
        string="Description")
    next_date = fields.Date(
        string="Next Date")
    lead_id = fields.Many2one(
        'crm.lead',
        string="Lead")
