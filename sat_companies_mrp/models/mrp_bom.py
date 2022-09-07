from odoo import models, fields, api, _

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    is_minute_point = fields.Boolean(
        string="Enable minute point")
    


class MrpBomline(models.Model):
    _inherit = 'mrp.bom.line'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale order")
