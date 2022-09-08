from odoo import models, fields, api, _

class ResPartnerZones(models.Model):
    _name = 'sale.order.bom'
    _inherit = 'mail.thread'
    _description = 'Sale order bom'

    name = fields.Char(
        string="Name",
        tracking=True)
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale order")
    bom_id = fields.Many2one(
        'mrp.bom',
        string="Mrp bom")
    bom_line_ids = fields.One2many(
        related="bom_id.bom_line_ids")
    product_id = fields.Many2one(
        'product.product',
        string="Product")
