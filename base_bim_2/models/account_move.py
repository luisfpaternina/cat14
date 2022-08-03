from odoo import api, fields, models


class BimAccountMove(models.Model):
    _inherit = "account.move"

    budget_id = fields.Many2one('bim.budget', 'Budjet', ondelete="restrict", domain="[('project_id','=',project_id)]")
    concept_id = fields.Many2one('bim.concepts', 'Concept', ondelete="restrict", domain="[('budget_id','=',budget_id),('type','=','departure')]")
    project_id = fields.Many2one('bim.project', 'Project', tracking=True, domain="[('company_id','=',company_id)]")
    workorder_id = fields.Many2one('bim.work.order', 'Work Order')
    maintenance_id = fields.Many2one('bim.maintenance', 'Maintenance', tracking=True)
    bim_classification = fields.Selection([('income', 'Income'), ('expense', 'Expense')], string='BIM Classification', index=True)
    include_for_bim = fields.Boolean()
    bim_multi_project = fields.Boolean(default=lambda self: self.env.company.bim_invoice_multiple_project)

    @api.model
    def default_get(self, fields):
        values = super().default_get(fields)
        if 'move_type' in values and values['move_type'] == 'in_refund':
            values['include_for_bim'] = self.env.company.bim_include_refund
        elif 'move_type' in values and values['move_type'] == 'in_invoice':
            values['include_for_bim'] = self.env.company.bim_include_invoice_purchase
        elif 'move_type' in values and values['move_type'] == 'out_invoice':
            values['include_for_bim'] = self.env.company.bim_include_invoice_sale
        return values

    @api.onchange('concept_id')
    def _onchange_concept_id(self):
        for record in self:
            if record.move_type in ['in_invoice', 'in_refund', 'in_receipt'] and not record.bim_multi_project:
                for line in record.invoice_line_ids:
                    line.concept_id = record.concept_id.id

    @api.onchange('budget_id')
    def _onchange_budget_id(self):
        for record in self:
            record.concept_id = False
            if record.move_type in ['in_invoice', 'in_refund', 'in_receipt'] and not record.bim_multi_project:
                for line in record.invoice_line_ids:
                    line.budget_id = record.budget_id.id
                    line.concept_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for record in self:
            record.budget_id = False
            record.concept_id = False
            if record.move_type in ['in_invoice', 'in_refund', 'in_receipt'] and not record.bim_multi_project:
                for line in record.invoice_line_ids:
                    line.budget_id = False
                    line.concept_id = False
                    line.analytic_account_id = record.project_id.analytic_id
                    line.project_id = record.project_id


class BimAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    budget_id = fields.Many2one('bim.budget', domain="[('id','in',budget_ids)]")
    concept_id = fields.Many2one('bim.concepts', 'Concept', domain="[('budget_id','=',budget_id),('type','=','departure')]")
    budget_ids = fields.Many2many('bim.budget', compute='_compute_budget_ids')
    bim_multi_project = fields.Boolean(related='move_id.bim_multi_project')
    project_id = fields.Many2one('bim.project')

    @api.onchange('product_id')
    def _onchange_concepts(self):
        for line in self:
            if not line.move_id.bim_multi_project:
                line.analytic_account_id = line.move_id.project_id.analytic_id
                line.budget_id = line.move_id.budget_id
                line.concept_id = line.move_id.concept_id
                line.project_id = line.move_id.project_id

    @api.onchange('budget_id')
    def _onchange_budget_id(self):
        for line in self:
            line.concept_id = False

    @api.depends('move_id.project_id','bim_multi_project','analytic_account_id','product_id')
    def _compute_budget_ids(self):
        for record in self:
            budget_list = []
            if not record.bim_multi_project and record.move_id.project_id:
                budget_list = record.move_id.project_id.budget_ids.ids
                record.analytic_account_id = record.move_id.project_id.analytic_id.id
                if not record.budget_id.id in record.move_id.project_id.budget_ids.ids:
                    record.project_id = False
                    record.budget_id = False
                    record.concept_id = False
                # record._onchange_concepts()
            elif record.bim_multi_project and record.analytic_account_id:
                project = self.env['bim.project'].search([('analytic_id','=',record.analytic_account_id.id)], limit=1)
                if project:
                    record.project_id = project
                    budget_list = project.budget_ids.ids
                    if not record.budget_id.id in project.budget_ids.ids:
                        record.budget_id = False
                        record.concept_id = False
                else:
                    record.project_id = False
                    record.budget_id = False
                    record.concept_id = False
            record.budget_ids = budget_list
