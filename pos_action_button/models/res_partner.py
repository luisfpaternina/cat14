from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # CAMPOS
    idvalidate = fields.Integer(
        string="Validate")
