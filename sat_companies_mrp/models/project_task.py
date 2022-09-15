from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime,date,timedelta
from datetime import date
import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def get_values_minute_point_from_sale(self):
        sale_obj = self.env['sale.order'].search([('name', '=', self.origin)])
        if sale_obj:
            for line in sale_obj.order_line:
                self.write({'checklist_line_ids': [(0, 0, {
                    'minute_point_id': line.minute_point_id.id,
                    })]
                    })
