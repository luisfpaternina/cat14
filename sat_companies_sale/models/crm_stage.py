# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CrmStage(models.Model):
    _inherit = 'crm.stage'

    oportunity_type_id = fields.Many2one(
        'crm.lead.type',
        string="Oportunity type")
