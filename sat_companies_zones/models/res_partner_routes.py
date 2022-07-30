# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartnerRoutes(models.Model):
    _name = 'res.partner.routes'
    _inherit = 'mail.thread'
    _description = 'Routes'
    _rec_name = 'code'

    name = fields.Char(
        string="Name",
        tracking=True)
    code = fields.Char(
        string="Code", 
        tracking=True,
        required=True,
        copy=False)
    country_id = fields.Many2one(
        'res.country',
        string="Country",
        tracking=True)
    route_type = fields.Selection([
        ('normal','Normal'),
        ('guard','Guard')],string="Route type",tracking=True)
    user_operator_id = fields.Many2one(
        'hr.employee',
        string="Operator notice")
    user_operator_greasing_id = fields.Many2one(
        'hr.employee',
        string="Operator greasing")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Responsable")
    zone_id = fields.Many2one(
        'res.partner.zones',
        string="Zone")
    users_ids = fields.Many2many('res.users',
        string="Users")
    zone_name = fields.Char(
        string="Zone name",
        related="zone_id.name")
    

    _sql_constraints = [
        ('code_uniq', 'unique (code)','This code already exists!')
    ]
    
    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
