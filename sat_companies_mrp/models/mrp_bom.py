from odoo import models, fields, api, _

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale order")
    minute_point_id = fields.Many2one(
        'maintenance.minute.point',
        string="Minute point")
    



class MrpBomline(models.Model):
    _inherit = 'mrp.bom.line'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale order")
