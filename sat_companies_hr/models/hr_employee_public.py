# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    delegation_id = fields.Many2one(
        'res.partner.delegation',
        string="Delegation")
    delegation_code = fields.Char(
        string="Code")
    c_accountant = fields.Char(
        string="C.Accountant")
    account_id = fields.Many2one(
        'account.account',
        string="C.Accountant")
    alarm_code = fields.Char(
        string="Alarm code")
    shirt_size = fields.Char(
        string="Shirt size")
    shoe_size = fields.Char(
        string="Shoe size")
    jersey_size = fields.Char(
        string="Jersey size")
    parka_size = fields.Char(
        string="Parka size")
    jacket_size = fields.Char(
        string="Jacket size")
    pants_size = fields.Char(
        string="Pants size")
    polo_size = fields.Char(
        string="Polo size")
    raincoat_size = fields.Char(
        string="Raincoat size")
    pda = fields.Boolean(
        string="PDA")
    online_service = fields.Boolean(
        string="Online services")
    supervisor = fields.Boolean(
        string="Supervisor")
    warehouse = fields.Char(
        string="Warehouse")
    workwear = fields.Boolean(
        string="Workwear")
    password = fields.Char(
        string="Password")
    imei = fields.Char(
        string="IMEI")
    type_driving_license = fields.Char(
        string="Type driving license")
    employee_type = fields.Many2one(
        'hr.employee.type',
        string="Employee type")
    is_maintainer = fields.Boolean(
        string="Is maintainer")
    category_id = fields.Many2one(
        'hr.employee.categories',
        string="Employee category")
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="Warehouse")
    code = fields.Char(
        string="Code",
        readonly=True,
        required=True,
        copy=False,
        default='New')
    employee_notes = fields.Text(
        string="Notes")


    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('employee.code') or 'New'
        result = super(HrEmployeePublic, self).create(vals)
        return result
    