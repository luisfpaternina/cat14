from odoo import models, fields, api, _

class Commissions(models.Model):
    _name = "commissions"
    _inherit = 'mail.thread'
    _description = "Commissions"

    name = fields.Char(
        string='Name',
        tracking=True)
    user_id = fields.Many2one(
        'res.users',
        string="Comercial",
        tracking=True)
    amount = fields.Float(
        string="Amount",
        tracking=True)
    description = fields.Text(
        string="Description",
        tracking=True)


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
