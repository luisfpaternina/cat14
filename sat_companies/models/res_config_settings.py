from markupsafe import string
from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    charge = fields.Char(
        string="Charge",
        readonly=False,
        config_parameter='sat_companies.charge')
    show_technical = fields.Boolean(
        string="Enable technical",
        related="company_id.show_technical",
        readonly=False,
        config_parameter='sat_companies.show_technical')
    is_potencial_client = fields.Boolean(
        string="Is potencial client",
        related="company_id.is_potencial_client",
        readonly=False,
        config_parameter='sat_companies.is_potencial_client')
    module_bim = fields.Boolean(
        string="BIM")
    module_bim_project = fields.Boolean(
        string="BIM")
    module_documents = fields.Boolean(
        string="Documents")
    module_sat_companies_quality = fields.Boolean(
        string="Quality")
    module_sat_companies_product_qr = fields.Boolean(
        string="QR generator gadgets")
    module_sat_companies_purchase = fields.Boolean(
        string="Purchases")
    module_sale_revision_history = fields.Boolean(
        string="Sale revision history")
    module_pc_stock_picking_ext = fields.Boolean(
        string="pc stock picking ext")
    has_rae = fields.Boolean(
        string="Has RAE",
        related="company_id.has_rae",
        readonly=False,
        config_parameter='sat_companies.has_rae')
    is_forecast_made = fields.Boolean(
        string="Is forecast made",
        related="company_id.is_forecast_made",
        readonly=False,
        config_parameter='sat_companies.is_forecast_made')
    

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('charge', self.charge)
        self.env['ir.config_parameter'].sudo().set_param('show_technical', self.show_technical)
        self.env['ir.config_parameter'].sudo().set_param('is_potencial_client', self.is_potencial_client)
        self.env['ir.config_parameter'].sudo().set_param('has_rae', self.has_rae)
        self.env['ir.config_parameter'].sudo().set_param('is_forecast_made', self.is_forecast_made)
        return res
