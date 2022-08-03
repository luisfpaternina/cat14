# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class BimListPriceAgreed(models.Model):
    _name = 'bim.list.price.agreed'
    _description = 'Agreed Price List'

    product_id = fields.Many2one('product.product', 'Product')
    price_agreed = fields.Float('Agreed Price')
    project_id = fields.Many2one('bim.project', string='Project')


