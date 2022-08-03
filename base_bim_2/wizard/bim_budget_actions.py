from odoo import api, fields, models, _

class BimBudgetAction(models.TransientModel):
    _name = 'bim.budget.actions.wizard'
    _description = 'Budgets Actions'

    def default_budget_ids(self):
        return self.env.context.get('active_ids', [])

    budget_ids = fields.Many2many('bim.budget', default=default_budget_ids)
    calculate_budget = fields.Boolean(default=False)
    change_budget_state = fields.Boolean(default=False)
    change_budget_type = fields.Boolean(default=True)
    budget_type = fields.Selection([('budget', 'Budget'),('certification', 'Certification'),
                                    ('execution', 'Execution'),('gantt', 'Programming')], string='New Budget Type')
    budget_state_id = fields.Many2one('bim.budget.state', string="New Budget State")

    def apply_changes(self):
        if self.change_budget_type:
            for budget in self.budget_ids:
                budget.type = self.budget_type
        if self.change_budget_state:
            for budget in self.budget_ids:
                budget.state_id = self.budget_state_id.id
        if self.calculate_budget:
            for budget in self.budget_ids:
                budget.update_amount()
