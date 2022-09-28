# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleSubscriptionStage(models.Model):
    _inherit = 'sale.subscription.stage'

    stage_code = fields.Char(
        string="Code")
    

    _sql_constraints = [
        ('code_uniq', 'unique (stage_code)','Code must be unique!')
    ]
