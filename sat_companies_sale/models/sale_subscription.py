# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    is_maintenance = fields.Boolean(
        string="Is a maintenance",
        tracking=True)
    type_contract = fields.Selection([
        ('normal','Normal'),
        ('all_risk','All risk')],string="Type of contract",tracking=True)
    show_technical = fields.Boolean(
        string="Enable technical",
        compute="compute_show_technical")
    
    @api.depends('partner_id')
    def compute_show_technical(self):
        show_technical = self.env['ir.config_parameter'].sudo().get_param('sat_companies.show_technical') or False
        self.show_technical = show_technical
