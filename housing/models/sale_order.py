from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_validate = fields.Boolean(string="Validate")
