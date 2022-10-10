from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from datetime import date
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    has_leave = fields.Boolean(
        string="Has a leave?",
        compute="check_has_leave")
    date_today = fields.Date(
        string="Date today",
        compute="current_date_today")
    supervisor_has_leave = fields.Boolean(
        string="supervisor has a leave?",
        compute="check_supervisor_leaves")
    has_users = fields.Boolean(
        string="Has users",
        compute="check_has_users")
    

    @api.depends('name')
    def current_date_today(self):
        today = date.today()
        self.date_today = today

    @api.depends('users_ids')
    def check_has_users(self):
        if self.users_ids:
            leave_obj = self.env['hr.leave'].search([('request_date_from', '=', self.date_today)])
            leave_obj_to = self.env['hr.leave'].search([('request_date_to', '=', self.date_today)])
            user_one = leave_obj.user_id.id
            user_two = leave_obj_to.user_id.id
            users = []
            users.append(self.users_ids.ids)
            x = users[0][0]
            if users:
                if user_one == x:
                    self.has_users = True
                elif user_two == x:
                    self.has_users = True
                else:
                    self.has_users = False
            else:
                self.has_users = False
        else:
            self.has_users = False
    
    @api.depends('users_ids')
    def check_has_leave(self):
        if len(self.users_ids) > 1:
            leave_obj = self.env['hr.leave'].search([('request_date_from', '=', self.date_today)])
            leave_obj_to = self.env['hr.leave'].search([('request_date_to', '=', self.date_today)])
            user_one = leave_obj.user_id.id
            user_two = leave_obj_to.user_id.id
            users = []
            users.append(self.users_ids.ids)
            x = users[0][1]
            if users:
                if user_one == x:
                    self.has_leave = True
                elif user_two == x:
                    self.has_leave = True
                else:
                    self.has_leave = False
            else:
                self.has_leave = False
        else:
            self.has_leave = False


    @api.depends('users_ids')
    def check_leaves_users(self):
        operator = self.product_id.techical_one_id.id
        leave_obj = self.env['hr.leave'].search([('user_id', '=', operator), ('request_date_from', '=', self.date_today)])
        leave_obj_to = self.env['hr.leave'].search([('user_id', '=', operator), ('request_date_to', '=', self.date_today)])
        if leave_obj or leave_obj_to:
            self.has_leave = True
        else:
            self.has_leave = False
    
    @api.depends('users_ids')
    def check_supervisor_leaves(self):
        supervisor = self.product_id.supervisor_zone_id.id
        leave_obj = self.env['hr.leave'].search([('user_id', '=', supervisor), ('request_date_from', '=', self.date_today)])
        leave_obj_to = self.env['hr.leave'].search([('user_id', '=', supervisor), ('request_date_to', '=', self.date_today)])
        if leave_obj or leave_obj_to:
            self.supervisor_has_leave = True
        else:
            self.supervisor_has_leave = False
    
    @api.constrains(
        'users_ids',
        'product_id',
        'has_users',
        'name')
    def validate_hr_leave_from_ot(self):
        for record in self:
            if record.has_users:
                raise ValidationError(_("The user has a leave"))
    
    @api.constrains(
        'users_ids',
        'product_id',
        'has_users',
        'name')
    def validate_leave_ot(self):
        for record in self:
            if record.has_leave:
                raise ValidationError(_("The user has a leave"))
