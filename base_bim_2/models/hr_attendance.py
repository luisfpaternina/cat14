from odoo import api, fields, models, _
from datetime import timedelta
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    project_id = fields.Many2one('bim.project', string='Project', domain="[('state_id.include_in_attendance','=',True)]")
    budget_id = fields.Many2one('bim.budget', string='Budget', domain="[('project_id','=',project_id)]")
    concept_id = fields.Many2one('bim.concepts', string='Concept', domain="[('budget_id','=',budget_id),('type','=','departure')]")

    bim_extra_hour_id = fields.Many2one('bim.extra.hour', string='Extra Hour')
    attendance_cost = fields.Float(string='Cost', compute='compute_attendance_cost', store=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True,
                                  default=lambda r: r.env.company.currency_id)
    hour_cost = fields.Float(string='Cost', compute='compute_attendance_cost', store=True)
    description = fields.Char()
    from_wizard = fields.Boolean(default=False)

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.budget_id = False

    @api.onchange('budget_id')
    def onchange_budget_id(self):
        self.concept_id = False

    @api.depends('worked_hours','bim_extra_hour_id')
    def compute_attendance_cost(self):
        for record in self:
            if record.bim_extra_hour_id and record.bim_extra_hour_id.value > 0:
                record.hour_cost = record.bim_extra_hour_id.value
            else:
                if record.employee_id.hour_cost > 0:
                    record.hour_cost = record.employee_id.hour_cost
                else:
                    if record.employee_id.total_hours_week > 0:
                        record.hour_cost = record.employee_id.wage_bim / (record.employee_id.total_hours_week * 4)
                    else:
                        record.hour_cost = 0
            record.attendance_cost = round(record.hour_cost * record.worked_hours,2)

    @api.model
    def create(self, vals):
        res = super(HrAttendance, self).create(vals)
        if res.from_wizard and res.env.company.server_hour_difference:
            hour_difference = res.env.company.server_hour_difference
            res.check_in += timedelta(hours=hour_difference)
            if res.check_out:
                res.check_out += timedelta(hours=hour_difference)
        if not 'project_id' in vals and not res.project_id:
            res.project_id = res.employee_id.default_bim_project.id
        return res