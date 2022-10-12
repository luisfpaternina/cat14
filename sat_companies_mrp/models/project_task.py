from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime,date,timedelta
from datetime import date
import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sale_id = fields.Many2one(
        'sale.order',
        string="Sale order",
        compute="compute_sale_order")
    order_line = fields.One2many(
        related="sale_id.order_line",
        string="Order lines")


    @api.model
    def get_work_records(self):
        for rec in self:
            lines = []
            sale_obj = rec.env['sale.order'].search([('id', '=', rec.sale_id.id)], limit=1)
            if sale_obj:
                for s in sale_obj.order_line:
                    vals = (0, 0, {
                        'name': s.name,
                    })
                    lines.append(vals)
                rec.work_line_ids = lines

    def compute_sale_order(self):
        sale_obj = self.env['sale.order'].search([('name', '=', self.origin)])
        if sale_obj:
            self.sale_id = sale_obj.id
        else:
            self.sale_id = False
