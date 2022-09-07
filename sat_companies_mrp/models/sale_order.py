from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mrp_bom_line_ids = fields.One2many(
        'mrp.bom.line',
        'sale_order_id',
        string="Bom lines")
