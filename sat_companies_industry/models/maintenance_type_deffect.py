# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MaintenanceTypeDeffect(models.Model):
    _name = 'maintenance.type.deffect'
    _inherit = 'mail.thread'
    _description = 'Type deffect'

    name = fields.Char(
        string="Name",
        tracking=True)
    description = fields.Text(
        string="Description",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        default=True)


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False