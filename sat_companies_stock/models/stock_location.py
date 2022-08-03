# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging


class StockLocation(models.Model):
    _inherit = 'stock.location'

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner")
    project_id = fields.Many2one(
        'project.project',
        string="Project")
