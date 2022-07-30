from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # CAMPOS
    age = fields.Integer(string="Age")
    gender = fields.Selection([
        ('male','Male'),
        ('famale','Famale')],string="Gender")
