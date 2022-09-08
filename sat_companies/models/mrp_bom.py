from odoo import models, fields, api, _

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale order")
    minute_point_id = fields.Many2one(
        'maintenance.minute.point',
        string="Minute point")
    is_minute_point = fields.Boolean(
        string="Enable minute point",
        compute="compute_is_minute_point")
    

    @api.depends('product_tmpl_id')
    def compute_is_minute_point(self):
        mp = self.env['ir.config_parameter'].sudo().get_param('sat_companies.is_minute_point') or False
        self.is_minute_point = mp
