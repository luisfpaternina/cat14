from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    code = fields.Char(
        string="Code")
