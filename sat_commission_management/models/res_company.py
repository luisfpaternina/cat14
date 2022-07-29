from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    terms = fields.Text(string="Terms")
    