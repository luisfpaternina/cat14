# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging


class ProjectTaks(models.Model):
    _inherit = 'project.task'

    product_id = fields.Many2one(
        'product.template',
        string="Gadget")
    is_conflictivea_pparatus = fields.Boolean(
        string="Is conflictive apparatus")


    def _compute_repeat(self):
        print('test')
        res = super(ProjectTaks, self)._compute_repeat()
        if self:
            product = self.product_id
            if product.is_recurring_task:
                self.recurring_task = product.is_recurring_task
                self.repeat_interval = product.repeat_interval
                self.repeat_unit = product.repeat_unit 
                self.repeat_on_month = product.repeat_on_month 
                self.repeat_on_year = product.repeat_on_year 
                self.repeat_day = product.repeat_day
                self.repeat_week = product.repeat_week
                self.repeat_weekday = 'mon'
                self.repeat_month = product.repeat_month
                self.repeat_until = product.repeat_until 
                self.repeat_number = product.repeat_number
                self.repeat_type = product.repeat_type
                self.mon = product.mon
                self.tue = product.tue
                self.wed = product.wed
                self.thu = product.thu
                self.fri = product.fri
                self.sat = product.sat
                self.sun = product.sun
            else:
                self.recurring_task = False
                self.repeat_interval = False
                self.repeat_unit = False
                self.repeat_type = False
                self.mon = False
                self.tue = False
                self.wed = False
                #self.repeat_weekday = 'mon'
                self.thu = False
                self.fri = False
                self.sat = False
                self.sun = False

        return self
