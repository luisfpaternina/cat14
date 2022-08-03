# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta


class LoadWeekHours(models.TransientModel):
    _name = "load.week.hours"
    _description = 'Load Week Hours'

    @api.model
    def default_get(self, fields):
        res = super(LoadWeekHours, self).default_get(fields)
        today = date.today()
        res['week_date'] = datetime.strftime((today - timedelta(days=today.weekday())), '%Y-%m-%d')
        context = self._context
        project = self.env['bim.project'].browse(context['active_id'])
        lines = []
        working_hours = self.env.user.company_id.working_hours
        for line in project.employee_line_ids:
            lines.append([0, 0, {
                'employee_id': line.employee_id.id,
                'hours1': working_hours,
                'extra1': 0,
                'hours2': working_hours,
                'extra2': 0,
                'hours3': working_hours,
                'extra3': 0,
                'hours4': working_hours,
                'extra4': 0,
                'hours5': working_hours,
                'extra5': 0,
                'hours6': 0,
                'hours7': 0,
            }])
        res['line_ids'] = lines
        res = self._convert_to_write(res)
        return res

    week_date = fields.Date('Mondays of the Week',
        help="Enter the Monday date of the week to which you want to load the hours")
    line_ids = fields.One2many('load.week.hours.line','wizard_id','Lines')

    def load_hours(self):
        context = self._context
        today = date.today()
        project = self.env['bim.project'].browse(context['active_id'])
        working_hours = self.env.user.company_id.working_hours
        project_timesheet = self.env['bim.project.employee.timesheet']
        year = self.week_date.year
        month = self.week_date.month
        day = self.week_date.day
        week_number = date(int(year), int(month), int(day)).strftime("%V")
        week_date = datetime.strptime(str(self.week_date), '%Y-%m-%d')
        start = datetime.strptime(str(self.week_date), '%Y-%m-%d') - timedelta(days=week_date.weekday())
        for line in self.line_ids:
            values = line.get_hours_line_data()
            total = line.hours1 + line.hours2 + line.hours3 + line.hours4 + line.hours5
            total_extra = line.extra1 + line.extra2 + line.extra3 + line.extra4 + line.extra5 + line.hours6 + line.hours7
            timesheets = project_timesheet.search([
                ('employee_id','=',values['employee_id']),
                ('week_number','=',week_number)
            ])
            ts_hours = sum(x.total_hours for x in timesheets)
            if (ts_hours + total) > 45:
                raise ValidationError(_('It is not possible to charge more than 45 hours in the same week to employee %s. You are trying to load %dh and currently have %dh loaded for the week of %s/%s/%s'%(line.employee_id.name, total, ts_hours, day, month, year)))
            existing_timesheet = timesheets.filtered(lambda r: r.project_id.id == project.id)
            if existing_timesheet:
                existing_timesheet.write({
                    'total_hours': total,
                    'total_extra_hours': total_extra,
                })
            else:
                project_timesheet.create({
                    'employee_id': values['employee_id'],
                    'date': self.week_date,
                    'week_start': datetime.strftime(start, '%Y-%m-%d'),
                    'week_end': datetime.strftime((start + timedelta(days=6)), '%Y-%m-%d'),
                    'total_hours': total,
                    'total_extra_hours': total_extra,
                    'project_id': project.id
                })
        return True


class LoadWeekHoursLine(models.TransientModel):
    _name = "load.week.hours.line"
    _description = 'Weekly Hours Loading Details'

    wizard_id = fields.Many2one('load.week.hours', 'Wizard')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    hours1 = fields.Float('Monday')
    hours2 = fields.Float('Tuesday')
    hours3 = fields.Float('Wednesday')
    hours4 = fields.Float('Thursday')
    hours5 = fields.Float('Friday')
    hours6 = fields.Float('Saturday')
    hours7 = fields.Float('Monday')
    extra1 = fields.Float('Monday Extra')
    extra2 = fields.Float('Tuesday Extra')
    extra3 = fields.Float('Wednesday Extra')
    extra4 = fields.Float('Thursday Extra')
    extra5 = fields.Float('Friday Extra')

    def get_hours_line_data(self):
        self.ensure_one()
        return {
            'employee_id': self.employee_id.id,
            'hours1': self.hours1,
            'hours2': self.hours2,
            'hours3': self.hours3,
            'hours4': self.hours4,
            'hours5': self.hours5,
            'hours6': self.hours6,
            'hours7': self.hours7,
            'extra1': self.extra1,
            'extra2': self.extra2,
            'extra3': self.extra3,
            'extra4': self.extra4,
            'extra5': self.extra5,

        }
