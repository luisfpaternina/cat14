from odoo import api, fields, models,_


class BimOpeningBalance(models.Model):
    _name = "bim.opening.balance"
    _description = "Bim Opening Balance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char("Reference", required=True, default=_('New'), copy=False)
    budget_id = fields.Many2one('bim.budget', 'Budjet', ondelete="restrict", domain="[('project_id','=',project_id)]", tracking=True, required=True)
    concept_id = fields.Many2one('bim.concepts', 'Concept', ondelete="restrict", domain="[('budget_id','=',budget_id),('type','=','departure')]", tracking=True)
    related_concept_id = fields.Many2one('bim.concepts', 'Concept', ondelete="restrict", domain="[('budget_id','=',budget_id),('type','=','departure')]", tracking=True)
    project_id = fields.Many2one('bim.project', 'Project', tracking=True, domain="[('company_id','=',company_id)]", ondelete="restrict", required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', related="project_id.currency_id", store=True)
    amount = fields.Float('Amount', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True, default=lambda self: self.env.user, readonly=True)
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.opening.balance') or "New"
        return super().create(vals)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for record in self:
            record.budget_id = False

    @api.onchange('budget_id')
    def _onchange_budget_id(self):
        for record in self:
            record.concept_id = False



