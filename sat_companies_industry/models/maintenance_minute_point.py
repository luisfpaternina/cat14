# -*- coding: utf-8 -*-
from numpy import concatenate
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MaintenanceMinutePoint(models.Model):
    _name = 'maintenance.minute.point'
    _inherit = 'mail.thread'
    _description = 'Minute point'
    _rec_name = 'concatenate'

    name = fields.Char(
        string="Name",
        tracking=True)
    code = fields.Char(
        string='Code',
        tracking=True,
        copy=False,)
    description = fields.Text(
        string="Description",
        tracking=True)
    type_deffect_id = fields.Many2one(
        'maintenance.type.deffect',
        string="Type of deffect",
        tracking=True)
    concatenate = fields.Char(
        string="Concatenate minute point")


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False

    @api.onchange('code', 'description')
    def concatenate_minute_point(self):
        self.concatenate = "%s %s" % (
            self.code if self.code else "",
            self.description if self.description else "")
