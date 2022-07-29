# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    partner_admin_id = fields.Many2one(
        'res.partner',
        string="Admin",
        tracking=True)
    active_name = fields.Char(
        string="Active name")
    is_admin = fields.Boolean(
        string="Is admin related",
        related="partner_admin_id.is_admin")
    partner_id = fields.Many2one(
        'res.partner',
        string="Client",
        tracking=True)
