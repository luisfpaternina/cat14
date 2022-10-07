from odoo import models, fields, api, _

class ResPartnerGuardZones(models.Model):
    _name = 'res.partner.guard.zones'
    _inherit = 'mail.thread'
    _description = 'Guard calendar'

    name = fields.Char(
        string="Guard zone name",
        tracking=True)
    code = fields.Char(
        string="Code", 
        tracking=True)
    delegation_id = fields.Many2one(
        'res.partner.delegation',
        string="Delegation",
        tracking=True)
    delegation_name = fields.Char(
        string="Delegation name",
        tracking=True,
        related="delegation_id.name")
    start_date = fields.Datetime(
        string="Start date")
    end_date = fields.Datetime(
        string="End date")
    user_id = fields.Many2one(
        'res.users',
        string="User")
    

    _sql_constraints = [
        ('code_uniq', 'unique (code)','This code already exists!')
    ]
    
    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
