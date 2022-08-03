# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime


class BimDepartment(models.Model):
    _description = "Project Department"
    _name = 'bim.department'
    _order = "id desc"

    def count_projects(self):
        for record in self:
            record.count_project_new = len(record.project_ids.filtered(lambda r: r.estado == '1'))
            record.count_project_estudy = len(record.project_ids.filtered(lambda r: r.estado == '2'))
            record.count_project_bidding = len(record.project_ids.filtered(lambda r: r.estado == '3'))
            record.count_project_revision = len(record.project_ids.filtered(lambda r: r.estado == '4'))
            record.count_project_awarded = len(record.project_ids.filtered(lambda r: r.project_state == 'in_process'))
            record.count_project_process = len(record.project_ids.filtered(lambda r: r.estado == '6'))
            record.count_project_lost = len(record.project_ids.filtered(lambda r: r.estado == '7'))
            record.count_project_quality = len(record.project_ids.filtered(lambda r: r.estado == '8'))
            record.count_project_delivered = len(record.project_ids.filtered(lambda r: r.estado == '9'))
    #         record.count_project_contracts_maintenance = len(record.project_ids.filtered(lambda r: r.maintenance_contract is True))

    name = fields.Char('Name', translate=True)
    project_ids = fields.One2many('bim.project','department_id','projects')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company,
                                 required=True)
    count_project_new = fields.Integer('New Projects', compute="count_projects")
    count_project_estudy = fields.Integer('Study Projects', compute="count_projects")
    count_project_bidding = fields.Integer('Bidding Projects', compute="count_projects")
    count_project_revision = fields.Integer('Review Projects', compute="count_projects")
    count_project_awarded = fields.Integer('Awarded Projects', compute="count_projects")
    count_project_process = fields.Integer('Process Projects', compute="count_projects")
    count_project_lost = fields.Integer('Lost Projects', compute="count_projects")
    count_project_quality = fields.Integer('Quality Projects', compute="count_projects")
    count_project_delivered = fields.Integer('Delivered Projects', compute="count_projects")
    count_project_contracts_maintenance = fields.Integer('Maintenance Contracts',)# compute="count_projects")
