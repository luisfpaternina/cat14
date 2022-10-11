from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bom_line_ids = fields.One2many(
        'mrp.bom.line',
        'sale_order_id',
        string ="Components",
        store = True)
    sale_bom_ids = fields.One2many(
        'sale.order.bom',
        'sale_order_id',
        string="Componets",
        compute="compute_components",
        store = True)
    order_bom_line = fields.One2many(
        'sale.order.line',
        related="order_line")

 


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bom_id = fields.Many2one(
        'mrp.bom',
        string="Mrp bom",
        compute="compute_bom_id")
    bom_line_ids = fields.One2many(
        related="bom_id.bom_line_ids")
    minute_point_id = fields.One2many(
        'maintenance.minute.point',
        'order_line_id',
        string="Minute point")
    is_domain_mp = fields.Boolean(
        string="Apply domain")


    @api.onchange('product_id')
    def domain_minute_points_mrp(self):
        for record in self:
            if record.product_id:
                record.minute_point_id = record.product_id.bom_ids.minute_point_id.ids
            else:
                record.minute_point_id = False
             
        
    @api.depends('product_id')
    def compute_bom_id(self):
        for line in self:
            if line.product_id:
                mrp_bom_obj = self.env['mrp.bom'].search([('product_id', '=', line.product_id.name)])
                if mrp_bom_obj:
                    for m in mrp_bom_obj:
                        line.write({'bom_id': m.id})
                else:
                    line.bom_id = False
            else:
                line.bom_id = False
    
    @api.depends('product_id')
    def compute_minute_point_id(self):
        for line in self:
            if line.product_id:
                mrp_bom_obj = self.env['mrp.bom'].search([('product_id', '=', line.product_id.name)])
                if mrp_bom_obj:
                    line.write({'minute_point_id': mrp_bom_obj.minute_point_id.id})
                else:
                    line.minute_point_id = False
            else:
                line.minute_point_id = False
