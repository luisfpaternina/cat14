# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import logging


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    task_id = fields.Many2one('project.task')