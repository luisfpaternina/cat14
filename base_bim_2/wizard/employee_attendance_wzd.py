# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta

class EmployeeAttendanceWzd(models.TransientModel):
    _name = "employee.attendance.wzd"
    _description = 'Employee Attendance'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        employee_id = self._context['active_id']
        res['employee_id'] = employee_id
        # today = datetime(date.today().year, date.today().month, date.today().day, 23, 59, 59)
        # today_last_attendance = self.env['hr.attendance'].search(
        #     [('check_out', '<=', today), ('employee_id', '=', employee_id)], order='check_out desc')
        # start_hour = self.env.company.hour_start_job
        # start_minute = self.env.company.hour_start_job
        # if today_last_attendance:
        #     start_hour = today_last_attendance[0].check_out.hour
        #     minutes = today_last_attendance[0].check_out.minute
        #     start_minute = 0
        #     while start_minute < minutes:
        #         start_minute +=5
        # res['hour_start_job'] = str(start_hour)
        # res['minute_start_job'] = str(start_minute)
        return res

    employee_id = fields.Many2one('hr.employee', required=True)
    project_id = fields.Many2one('bim.project', string='Project', domain="[('state_id.include_in_attendance','=',True)]")
    budget_id = fields.Many2one('bim.budget', string='Budget', domain="[('project_id','=',project_id)]")
    concept_id = fields.Many2one('bim.concepts', string='Concept', domain="[('budget_id','=',budget_id),('type','=','departure')]")
    date_attendance = fields.Date(default=lambda e: fields.Date.today(), required=True)
    hour_start_job = fields.Selection(
        [('0', '00'), ('1', '01'), ('2', '02'), ('3', '03'), ('4', '04'), ('5', '05'), ('6', '06'), ('7', '07'),
         ('8', '08'), ('9', '09'), ('10', '10'), ('11', '11'), ('12', '12'),
         ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
         ('21', '21'), ('22', '22'), ('23', '23')], required=True)
    minute_start_job = fields.Selection(
        [('0', '00'), ('5', '05'), ('10', '10'), ('15', '15'), ('20', '20'), ('25', '25'), ('30', '30'),
         ('35', '35'), ('40', '40'), ('45', '45'), ('50', '50'), ('55', '55')], default=lambda self: self.env.company.minute_start_job, required=True)
    bim_extra_hour_id = fields.Many2one('bim.extra.hour', string='Extra Hour')
    description = fields.Char()
    in_out = fields.Boolean(default=True, string="In/Out")
    working_hours = fields.Float('Working Hours', default=lambda self: self.env.company.working_hours)

    def action_register_attendance(self):
        if self.employee_id.hour_cost <= 0:
            raise UserError(_("It is not possible to register Attendance if the Employee does not have hour cost defined!"))
        year = self.date_attendance.year
        month = self.date_attendance.month
        day = self.date_attendance.day
        hour = int(self.hour_start_job)
        minute = int(self.minute_start_job)
        check_in = datetime(year,month,day, hour, minute)
        check_out = False
        if self.in_out:
            check_out = check_in + timedelta(hours=int(self.working_hours))
            minutes_str = str(self.working_hours).split('.')[1]
            minutes = int(minutes_str)
            if minutes > 0:
                if len(minutes_str) > 1:
                    minutes = int(minutes_str[:2])
                    minutes = minutes * 6 / 10
                else:
                    minutes = minutes * 60 / 10
                check_out = check_out + timedelta(minutes=int(minutes))

        self.env['hr.attendance'].create({
            'project_id': self.project_id.id,
            'budget_id': self.budget_id.id,
            'concept_id': self.concept_id.id,
            'employee_id': self.employee_id.id,
            'check_in': check_in,
            'from_wizard': True,
            'check_out': check_out,
            'description': self.description,
            'bim_extra_hour_id': self.bim_extra_hour_id.id or False,
        })

    @api.onchange('date_attendance')
    def onchange_date_attendance(self):
        if self.date_attendance:
            today = datetime(self.date_attendance.year, self.date_attendance.month, self.date_attendance.day, 23, 59, 59)
            last_attendances = self.env['hr.attendance'].search(
                [('check_out', '<=', today), ('employee_id', '=', self.employee_id.id)], order='check_out desc')
            start_hour = self.env.company.hour_start_job
            start_minute = self.env.company.minute_start_job
            if last_attendances:
                for attendance in last_attendances:
                    if attendance.check_out.day == today.day and attendance.check_out.month == today.month and attendance.check_out.year == today.year:
                        start_hour = attendance.check_out.hour - self.env.company.server_hour_difference
                        if start_hour >= 24:
                            start_hour -= 24
                            self.date_attendance += timedelta(days=1)
                        minutes = attendance.check_out.minute
                        start_minute = 0
                        while start_minute < minutes:
                            start_minute += 5
                        break
            self.hour_start_job = str(start_hour)
            self.minute_start_job = str(start_minute)
        else:
            self.hour_start_job = self.env.company.hour_start_job
            self.minute_start_job = self.env.company.minute_start_job