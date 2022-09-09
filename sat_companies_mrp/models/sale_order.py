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


    @api.depends('order_line','partner_id')
    def compute_components(self):
        for rec in self:
            lines = []
            for p in rec.order_line:
                vals = (0, 0, {
                    'product_id': p.product_id.id,
                    'bom_id': p.bom_id.id,
                })
                lines.append(vals)
            rec.sale_bom_ids = lines




class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bom_id = fields.Many2one(
        'mrp.bom',
        string="Mrp bom",
        compute="compute_bom_id")
    bom_line_ids = fields.One2many(
        related="bom_id.bom_line_ids")


    @api.depends('product_id')
    def compute_bom_id(self):
        for line in self:
            if line.product_id:
                mrp_bom_obj = self.env['mrp.bom'].search([('product_id', '=', line.product_id.name)])
                if mrp_bom_obj:
                    line.write({'bom_id': mrp_bom_obj.id})
                else:
                    line.bom_id = False
            else:
                line.bom_id = False
