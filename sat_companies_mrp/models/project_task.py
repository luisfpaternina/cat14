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


    def compute_sale_order(self):
        sale_obj = self.env['sale.order'].search([('name', '=', self.origin)])
        if sale_obj:
            self.sale_id = sale_obj.id
        else:
            self.sale_id = False
