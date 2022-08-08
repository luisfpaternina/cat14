from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    terms = fields.Text(
        string="Terms")
    show_technical = fields.Boolean(
        string="Enable technical")
    is_potencial_client = fields.Boolean(
        string="Is potencial client")
    has_rae = fields.Boolean(
        string="Has RAE")
    is_forecast_made = fields.Boolean(
        string="Is forecast made")
    user_operator_id = fields.Many2one(
        'res.users',
        string="Users")
    is_qr_required = fields.Boolean(
        string="Is QR required?")
    