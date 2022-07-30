# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    route_id = fields.Many2one(
        'res.partner.routes',
        string="Normal route")
    route_type_id = fields.Many2one(
        'res.partner.routes',
        string="Guard route")
    product_ids = fields.Many2many(
        'product.template',
        string="Gadgets")
    zones_ids = fields.Many2many(
        'res.partner.zones',
        string="Zones")
    routes_ids = fields.Many2many(
        'res.partner.routes',
        string="Routes")
