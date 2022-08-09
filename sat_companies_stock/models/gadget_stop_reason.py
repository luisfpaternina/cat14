# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GadgetStopReason(models.Model):
    _name = 'gadget.stop.reason'
    _inherit = 'mail.thread'
    _description = 'Gadget stop reason'

    name = fields.Char(
        string="Name",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        tracking=True,
        default=True)
    description = fields.Text(
        string="Description")

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
