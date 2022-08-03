# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BimAjustBudgetWzd(models.TransientModel):
    _name = 'bim.ajust.budget.wzd'
    _description = 'Adjust Budget'

    @api.model
    def default_get(self, fields_list):
        res = super(BimAjustBudgetWzd, self).default_get(fields_list)
        budget = self.env['bim.budget'].search([('id', '=', self._context.get('active_id'))])
        res['budget_id'] = budget.id
        res['amount'] = budget.balance
        return res

    budget_id = fields.Many2one(comodel_name="bim.budget", string="Budget")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company,
                                 readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.company.currency_id)
    amount = fields.Float(string="Amount")
    new_amount = fields.Float(string="New Amount")
    fixed = fields.Float(string="Fixed Amount")
    percent = fields.Float(string="Percentage")

    materials = fields.Boolean(string="Materials", default=True)
    work_hand = fields.Boolean(string="Labor", default=True)
    equipment = fields.Boolean(string="Equipment", default=True)

    service = fields.Boolean(string="Services", default=False)
    functions = fields.Boolean(string="Functions", default=False)
    duplicate = fields.Boolean(string="Duplicate Budget", default=False)

    type = fields.Selection(string="Modify by", selection=[('percent', 'Percentage'), ('fixed', 'Fixed Amount'), ('amount', 'Total')],
                                  default='percent')
    type_ajust = fields.Selection(string="Adjust", selection=[('quant', 'Quantity'), ('amount', 'Price')], default='amount')

    @api.onchange('new_amount')
    def _onchange_new_amount(self):
        if self.new_amount > 0 and self.amount > 0:
            percent = (((self.new_amount - self.amount) / self.amount) * 100) + 100
            self.percent = abs(percent)

    @api.onchange('percent')
    def _onchange_percent(self):
        new_amount = (self.percent * self.amount) / 100
        self.new_amount = new_amount

    def load_ajust(self):
        if not self.materials and not self.work_hand and not self.equipment:
            raise UserError(_("At least you have to select a Concept"))
        if self.duplicate:
           budget = self.budget_id.copy()
        else:
            budget = self.budget_id
        concepts = self.env['bim.concepts'].search([('budget_id', '=', budget.id),('type', 'not in', ('chapter', 'departure'))])
        filter = []
        if self.materials:
            filter.append('material')
        if self.work_hand:
            filter.append('labor')
        if self.equipment:
            filter.append('equip')
        concepts_affected = concepts.filtered(lambda r: r.type in filter)
        if self.type == 'percent':
            if self.percent <= 0:
                raise UserError(_("Value must be greater than zero"))
            else:
                percent = self.percent - 100
            for concept in concepts_affected:
                if self.type_ajust == 'amount':
                    concept.amount_fixed = concept.amount_fixed + (concept.amount_fixed * percent / 100)
                else:
                    concept.quantity = concept.quantity + (concept.quantity * percent / 100)
        elif self.type == 'amount':
            factor = 1
            if self.amount > 0:
                factor = self.new_amount / self.amount
            if self.new_amount <= 0:
                raise UserError(_("Value must be greater than zero"))
            # Verificación del nuevo monto total del presupuesto
            for concept in concepts_affected:
                if self.type_ajust == 'amount':
                    concept.amount_fixed = concept.amount_fixed * factor
                else:
                    concept.quantity = concept.quantity * factor

        else:
            for concept in concepts_affected:
                if self.type_ajust == 'amount':
                    tmp = concept.amount_fixed + self.fixed
                    concept.amount_fixed = tmp if tmp > 0 else 0
                else:
                    tmp = concept.quantity + self.fixed
                    concept.quantity = tmp if tmp > 0 else 0
        budget.update_amount()
        msg = "Budget modify in %s" % (budget.balance)
        budget.sudo().message_post(body=msg)
        if self.duplicate:
            action = self.env.ref('base_bim_2.action_bim_budget').sudo().read()[0]
            action['views'] = [(False, "form")]
            action['res_id'] = budget.id
            return action

    @api.onchange('type')
    def onchange_type(self):
        for record in self:
            if record.type == 'amount':
                record.type_ajust = 'amount'
                record.materials = True
                record.work_hand = True
                record.equipment = True
