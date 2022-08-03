# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime


class BimQualityControlPlan(models.Model):
    _description = "Inspection Type"
    _name = 'bim.quality.control.plan'
    _order = "id desc"

    name = fields.Char(default=_("New"))
    description = fields.Char(required=True, string="Description")
    code = fields.Char(string="Code")
    date = fields.Date(default=fields.Date.today,required=True, string="Date")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company, readonly=True)
    project_id = fields.Many2one('bim.project', 'Project', tracking=True, domain="[('company_id','=',company_id)]", required=True)
    control_plan_lines = fields.One2many('bim.quality.control.plan.line','plan_id')
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True, default=lambda self: self.env.user)

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.quality.control.plan') or "New"
        return super().create(vals)

    def action_view_control_lines(self):
        action = self.env.ref('base_bim_2.action_bim_quality_control_line').sudo().read()[0]
        if len(self.control_plan_lines) > 0:
            action['domain'] = [('id', 'in', self.control_plan_lines.ids)]
            action['context'] = {'default_plan_id': self.id}
        else:
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Control Plan',
                'res_model': 'bim.quality.control.plan.line',
                'view_mode': 'tree',
                'domain': [('id', 'in', self.control_plan_lines.ids)],
                'target': 'current',
                'context': {'default_plan_id': self.id}
            }
        return action

class BimQualityControlPlanLine(models.Model):
    _description = "Inspection Type"
    _name = 'bim.quality.control.plan.line'
    _order = "id desc"

    plan_id = fields.Many2one('bim.quality.control.plan', ondelete="cascade")

    def default_code(self):
        plan_id = self._context['active_id']
        plan_lines = self.env['bim.quality.control.plan'].browse(plan_id).control_plan_lines
        return len(plan_lines) + 1

    code = fields.Integer(string="Code", default=default_code)
    activity = fields.Text(string="Activity", required=True)
    inspection_type_id = fields.Many2one('bim.inspection.type', ondelete="restrict", required=True)
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True, default=lambda self: self.env.user)
    characteristic = fields.Text(string="Characteristic", required=True)
    frequency = fields.Char(string="Frequency", required=True)
    criterion = fields.Text(string="Characteristic", required=True)
    reference = fields.Text(string="Reference")
    doc_ids = fields.Many2many('bim.documentation', string="Attachments")
    checklist_ids = fields.Many2many('bim.checklist', string="Check Lists")
    register_type_id = fields.Many2one('bim.register.type', ondelete="restrict", required=True)
    register_related = fields.Text()
    inspection_ime = fields.Text()

