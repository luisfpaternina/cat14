from odoo import models, fields, api, _

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    partner_type_id = fields.Many2one(
        'res.partner.type',
        string="Partner type",
        related="partner_id.partner_type_id")
