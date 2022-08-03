from signal import valid_signals
from odoo import models, fields, api
from datetime import tzinfo, timedelta, datetime

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    sale_type_origin_id = fields.Many2one(
        'sale.order.type',
        'Sale Type Origin')
    sale_order_id = fields.Many2one(
        'sale.order',
        'Sale Order')
    start_date_project = fields.Datetime(
        'Start date project')
    location_count = fields.Integer(
        string="Location count",
        compute="compute_count")


    def compute_count(self):
        for record in self:
            record.location_count = self.env['stock.location'].search_count([('project_id', '=', self.id)])


    def get_location(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Locations',
            'view_mode': 'tree',
            'res_model': 'stock.location',
            'domain': [('project_id', '=', self.id)],
            'context': "{'create': False}"
        }


    def update_fields_service_dates(self):
        for record in self:
            dates_begin = [x.planned_date_begin for x in record.task_ids]
            if dates_begin[0]:
                date_min = min(dates_begin)
                diff_dates =record.start_date_project - date_min
                for task in record.task_ids:
                    if task.planned_date_begin and task.planned_date_end:
                        if date_min == task.planned_date_begin:
                            task.planned_date_begin = record.start_date_project
                            task.planned_date_end = task.planned_date_end + timedelta(days=diff_dates.days)
                        else:
                            task.planned_date_begin = task.planned_date_begin + timedelta(days=diff_dates.days)
                            task.planned_date_end = task.planned_date_end + timedelta(days=diff_dates.days)


    def write(self,vals):
        update_dates = False
        if 'start_date_project' in vals:
            update_dates = True
        res = super(ProjectProject, self).write(vals)
        for record in self:
            if update_dates == True:
                record.update_fields_service_dates()

        return res
