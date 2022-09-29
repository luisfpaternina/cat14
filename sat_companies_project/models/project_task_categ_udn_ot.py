# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskCategUdn(models.Model):
    _name = 'project.task.categ.udn'
    _inherit = 'mail.thread'
    _description = 'Category Udn OT'

    name = fields.Char(
        string="Name",
        tracking=True)
    code = fields.Char(
        string="Code",
        tracking=True)
    description = fields.Char(
        string="Description",
        tracking=True)
    ot_type_id = fields.Many2one(
        'sale.order.type',
        string="OT type")
    is_normative = fields.Boolean(
        string="Normative")
    is_user = fields.Boolean(
        string="Is user")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Supervisor")
    user_ids = fields.Many2many(
        'res.users',
        string="Users")
    #user_id = fields.Many2one(
    #    'res.users',
    #    string="User/supervisor")
    

    @api.onchange('name','code')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
        self.code = self.code.upper() if self.code else False

    #Limpiar valores campos listado categorías UDN
    @api.onchange('is_normative', 'is_user', 'employee_id')
    def _onchange_is_normative_user_employee(self):
        if self.is_normative == False:
            self.employee_id = False
            self.is_user = False
        if self.is_user == False:
            self.employee_id = False