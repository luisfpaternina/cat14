from odoo import models, fields, api, _

class CommissionsConcepts(models.Model):
    _name = "commissions.concepts"
    _inherit = 'mail.thread'
    _description = "Commissions concepts"

    name = fields.Char(
        string='Name',
        tracking=True)
    active = fields.Boolean(
        string="Active")
    amount = fields.Float(
        string="Amount",
        tracking=True)
    description = fields.Text(
        string="Description",
        tracking=True)
    is_client_number = fields.Boolean(
        string="Required number clients")


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
