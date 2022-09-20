from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    sale_type_origin_id = fields.Many2one('sale.order.type','Sale Type Origin')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
