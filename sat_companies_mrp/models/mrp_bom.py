from odoo import models, fields, api, _

class MrpBom(models.Model):
    _inherit = 'mrp.bom'


    is_minute_point = fields.Boolean(
        string="Enable minute point")
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale order")
    order_line_id = fields.Many2one(
        'sale.order.line',
        string="Order line")
    minute_point_id = fields.One2many(
        'maintenance.minute.point',
        'bom_id',
        string="Minute point")
    
    @api.onchange('product_tmpl_id')
    def get_product_id(self):
        for rec in self:
            product_obj = rec.env['product.product'].search([('name', '=', rec.product_tmpl_id.name)], limit=1)
            if product_obj:
                rec.write({'product_id': product_obj.id})

    @api.onchange('product_tmpl_id')
    def type_ldm_in_components(self):
        for record in self:
            if record.product_tmpl_id:
                record.type = 'phantom'


class MrpBomline(models.Model):
    _inherit = 'mrp.bom.line'

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale order")
