from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_minute_point = fields.Boolean(
        string="Enable minute point")
    