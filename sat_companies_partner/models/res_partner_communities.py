# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartnerCommunities(models.Model):
    _name = 'res.partner.communities'
    _inherit = 'mail.thread'
    _description = 'Communities'

    name = fields.Char(
        string="Name",
        tracking=True)
    partner_id = fields.Many2one(
        'res.partner',
        string="Contact")
    partner_community_id = fields.Many2one(
        'res.partner',
        string="Community")
    is_community = fields.Boolean(
        string="Is community",
        related="partner_community_id.is_community")
    

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
