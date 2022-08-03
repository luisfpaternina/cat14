# -*- coding: utf-8 -*-
from odoo import api, fields, models


class BimProject(models.Model):
    _inherit = 'bim.project'

    @api.depends('project_project_ids')
    def _compute_projects_count(self):
        for project in self:
            project.projects_count = len(project.project_project_ids)

    project_project_ids = fields.One2many('project.project', 'project_id', 'Projects')
    projects_count = fields.Integer('Nº Projects', compute=_compute_projects_count)

    @api.model
    def create(self, vals):
        res = super(BimProject, self).create(vals)
        project_obj = self.env['project.project']
        project_obj.create({
            'name': vals['nombre'],
            'partner_id': vals['customer_id'],
            'user_id': vals['user_id'],
            'project_id': res.id,
            'analytic_account_id': vals['analytic_id']
        })
        return res

    def action_view_project_project(self):
        projects = self.mapped('project_project_ids')
        action = self.env.ref('project.open_view_project_all_config').read()[0]
        action['domain'] = [('id', 'in', projects.ids)]
        action['context'] = {'default_project_id': self.id}
        return action
