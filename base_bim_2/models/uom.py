from odoo import fields, models, _


class UomUom(models.Model):
    _inherit = 'uom.uom'

    alt_names = fields.Char('Alternative names', help='Possible names by which this unit of measure can be searched.')
