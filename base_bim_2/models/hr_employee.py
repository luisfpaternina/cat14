# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

# class HrEmployeeBimPublic(models.Model):
#     _inherit = 'hr.employee.public'
#
#     wage_bim = fields.Float('BIM Salary')

class HrEmployeeBimBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    wage_bim = fields.Float('BIM Salary')
    default_bim_project = fields.Many2one('bim.project', string='Default Project')
    total_hours_week = fields.Float(compute='compute_total_hours_week')
    hour_cost = fields.Float(string='Hour Cost')
    bim_resource_id = fields.Many2one('product.product', domain="[('type','=','service')]")

    def compute_total_hours_week(self):
        for record in self:
            total = 0
            for line in record.resource_calendar_id.attendance_ids:
                total += line.hour_to - line.hour_from
            record.total_hours_week = total

class HrEmployeeBim(models.Model):
    _inherit = 'hr.employee'

    wage_bim = fields.Float('BIM Salary')
    default_bim_project = fields.Many2one('bim.project', string='Default Project')
    total_hours_week = fields.Float(compute='compute_total_hours_week')
    hour_cost = fields.Float(string='Hour Cost')
    bim_resource_id = fields.Many2one('product.product', domain="[('type','=','service')]")

    def compute_total_hours_week(self):
        for record in self:
            total = 0
            for line in record.resource_calendar_id.attendance_ids:
                total += line.hour_to - line.hour_from
            record.total_hours_week = total
