from odoo import models, fields, api, _

class ResBank(models.Model):
    _inherit = 'res.partner.bank'

    is_default = fields.Boolean(
        string="Is default")
