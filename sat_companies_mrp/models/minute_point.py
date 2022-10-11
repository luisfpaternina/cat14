from odoo import models, fields, api, _

class MaintenanceMinutePoint(models.Model):
    _inherit = 'maintenance.minute.point'

    order_line_id = fields.Many2one(
        'sale.order.line',
        string="Order line")
    bom_id = fields.Many2one(
        'mrp.bom',
        string ="Bom")
    is_domain = fields.Boolean(
        string="Domain")
