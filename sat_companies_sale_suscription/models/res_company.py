from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    partner_manager_id = fields.Many2one(
        'res.partner',
        string="Partner manager")
