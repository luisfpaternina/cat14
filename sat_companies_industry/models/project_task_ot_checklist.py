# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import datetime
import logging

class ProjectTaskOtChecklist(models.Model):
    _name = 'project.task.ot.checklist'
    _inherit = 'mail.thread'
    _description = 'OT checklist'

    name = fields.Char(
        string="Name",
        tracking=True)
    location = fields.Char(
        string="Location",
        tracking=True)
    accomplished = fields.Selection([
        ('yes','Yes'),
        ('Not','Not')],string="Accomplished", tracking=True)
    code = fields.Char(
        string="Code")
    check_1 = fields.Boolean(
        string="January")
    check_2 = fields.Boolean(
        string="February")
    check_3 = fields.Boolean(
        string="March")
    check_4 = fields.Boolean(
        string="April")
    check_5 = fields.Boolean(
        string="May")
    check_6 = fields.Boolean(
        string="June")
    check_7 = fields.Boolean(
        string="July")
    check_8 = fields.Boolean(
        string="August")
    check_9 = fields.Boolean(
        string="September")
    check_10 = fields.Boolean(
        string="October")
    check_11 = fields.Boolean(
        string="November")
    check_12 = fields.Boolean(
        string="December")
    line_number = fields.Char(
        string="N° line",
        copy=False)
    location_id = fields.Many2one(
        'project.task.ot.checklist.location',
        string="Location")
    user_id = fields.Many2one(
        'res.users',
        string="Operator")
    task_id = fields.Many2one(
        'project.task',
        string="Task")
    month_date = fields.Char(
        string="Month",
        compute="calculate_month")
    is_january = fields.Boolean(
        string="Is January")
    is_february = fields.Boolean(
        string="Is February")
    is_march = fields.Boolean(
        string="Is March")
    is_april = fields.Boolean(
        string="Is April")
    is_may = fields.Boolean(
        string="Is May")
    is_june = fields.Boolean(
        string="Is June")
    is_july = fields.Boolean(
        string="Is July")
    is_august = fields.Boolean(
        string="Is August")
    is_september = fields.Boolean(
        string="Is September")
    is_october = fields.Boolean(
        string="Is October")
    is_november = fields.Boolean(
        string="Is November")
    is_december = fields.Boolean(
        string="Is December")


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False


    @api.depends('create_date')
    def calculate_month(self):
        for record in self:
            dt = datetime.datetime.today()
            record.month_date = dt.month
