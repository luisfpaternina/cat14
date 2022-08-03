# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class ApuProductTemplate(models.Model):
    _inherit = 'product.template'

    resource_type = fields.Selection(
        [('M', 'Material'),
         ('H', 'Labor'),
         ('Q', 'Equipment'),
         ('S', 'Sub-Contract'),
         ('HR', 'Tool'),
         ('A', 'Administrative')],
        'Resourse Type', default='M')

    social_law = fields.Boolean('Social Law')
    last_sec = fields.Integer("Last sec reg")
    document_ids = fields.One2many('product.document.line', 'product_id', string='Documents')
    change_ids = fields.One2many('product.change.line', 'product_id', string='Changes')
    id_bim = fields.Char("BIM ID")
    bim_purchase_ids = fields.One2many('bim.product.purchase', 'template_id')

    @api.onchange('resource_type')
    def onchange_resource(self):
        if self.resource_type in ['M','Q'] and self.type == 'service':
            self.type = 'product'

class BimProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('resource_type')
    def onchange_resource(self):
        if self.resource_type in ['M','Q'] and self.type == 'service':
            self.type = 'product'

    def _get_product_bim_cost_list(self, partner_id=False, state_id=False):
        cost_line_ids = self.env['bim.cost.list.line'].search([('product_id','=',self.id)])
        product_cost = False
        if partner_id:
            for line in cost_line_ids.filtered_domain([('cost_id.partner_id','=',partner_id.id)]):
                product_cost = line.price
                break
        if state_id and not product_cost:
            for line in cost_line_ids.filtered_domain([('cost_id.state_id','=',state_id.id)]):
                product_cost = line.price
                break
        return product_cost

class ProductDocumentBim(models.Model):
    _name = 'product.document.line'
    _description = "Product Document Line"

    name = fields.Char('Name')
    comprobante_01_name = fields.Char("Attachment Name")
    comprobante_01 = fields.Binary(
        string=('Attachment'),
        copy=False,
        attachment=True,
        help='Voucher 01')
    entry_date = fields.Datetime('Entry Date', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Responsable',default=lambda self: self.env.user)
    product_id = fields.Many2one('product.template', string="Product", ondelete='cascade')


class ProductChangeBim(models.Model):
    _name = 'product.change.line'
    _description = "Product Change Line"

    product_id = fields.Many2one('product.product', string='Products')
    qty = fields.Float("Quantity")
    code_id = fields.Many2one('product.product', string='Code')
    position = fields.Integer("Position")
    product_id = fields.Many2one('product.template', string="Product", ondelete='cascade')


class BimProductPurchase(models.Model):
    _name = 'bim.product.purchase'
    _description = "Bim Product Purchase"

    purchase_id = fields.Many2one('purchase.order', required=True, ondelete='cascade')
    template_id = fields.Many2one('product.template', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade')
    project_id = fields.Many2one('bim.project', required=True, ondelete='cascade')
    supplier_id = fields.Many2one('res.partner', required=True)
    purchase_price = fields.Float(required=True)
    date = fields.Date()
    quantity = fields.Float(required=True)


