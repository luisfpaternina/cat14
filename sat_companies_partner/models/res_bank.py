from odoo import models, fields, api, _

class ResBank(models.Model):
    _inherit = 'res.partner.bank'

    _sql_constraints = [
        ('unique_number', 'Check(1=1)', 'Account Number must be unique'),
    ]
