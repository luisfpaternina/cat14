from odoo import models, fields, api, _

class ResPartnerZones(models.Model):
    _name = 'res.partner.zones'
    _inherit = 'mail.thread'
    _description = 'Zones'
    _rec_name = 'code'

    name = fields.Char(
        string="Zone's name",
        tracking=True)
    code = fields.Char(
        string="Code", 
        tracking=True,
        required=True,
        copy=False)
    country_id = fields.Many2one('res.country',
        string="Country",
        tracking=True)
    user_id = fields.Many2one('res.users',
        string="Responsable",
        tracking=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string="Operator notice",
        tracking=True)
    employee_greasing_id = fields.Many2one(
        'hr.employee',
        string="Greasing operator",
        tracking=True)
    guard_zone = fields.Char(
        string="Guard zone",
        tracking=True)
    product_line_ids = fields.One2many(
        'res.partner.zones.lines',
        'zone_id',
        string="Gadgets",
        tracking=True)
    employee_greasing_code = fields.Char(
        string="Cod.Ope.",
        tracking=True,
        related="employee_greasing_id.code")
    employee_notice_code = fields.Char(
        string="Cod.Ope.",
        tracking=True,
        related="employee_id.code")
    delegation_id = fields.Many2one(
        'res.partner.delegation',
        string="Delegation",
        tracking=True)
    delegation_name = fields.Char(
        string="Delegation name",
        tracking=True,
        related="delegation_id.name")
    guard_zone_id = fields.Many2one(
        'res.partner.guard.zones',
        string="Guard zone",
        tracking=True)
    guard_zone_name = fields.Char(
        string="guard zone name",
        tracking=True,
        related="guard_zone_id.name")
    responsable_id = fields.Many2one(
        'hr.employee',
        string="Responsable",
        tracking=True)
    responsable_code = fields.Char(
        "Code responsable",
        tracking=True,
        related="responsable_id.code")
    users_ids = fields.Many2many('res.users',
        string="Users")


    _sql_constraints = [
        ('code_uniq', 'unique (code)','This code already exists!')
    ]

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
    


class ResPartnerZonesLines(models.Model):
    _name = 'res.partner.zones.lines'
    _inherit = 'mail.thread'
    _description = 'Zones lines'

    zone_id = fields.Many2one(
        'res.partner.zones',
        string="Zone",
        tracking=True)
    product_id = fields.Many2one(
        'product.template',
        string="Gadgets",
        tracking=True)
