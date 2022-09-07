from markupsafe import string
from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_minute_point = fields.Boolean(
        string="Is potencial client",
        related="company_id.is_minute_point",
        readonly=False,
        config_parameter='sat_companies_mrp.is_minute_point')
    

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('is_minute_point', self.is_minute_point)
        return res
