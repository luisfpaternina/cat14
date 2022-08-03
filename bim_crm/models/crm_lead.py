# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    bim_order_ids = fields.One2many('bim.project', 'opportunity_id', string='Projects')
    bim_order_amount_total = fields.Monetary(compute='_compute_project_data', string="Sum of Orders",
                                        help="Untaxed Total of Confirmed Orders", currency_field='company_currency')

    bim_quotation_count = fields.Integer(string="Number of Sale Orders", compute='_compute_project_data',)

    def action_view_bim_project(self):
        action = self.env.ref('base_bim_2.action_bim_proect').sudo().read()[0]
        action['context'] = {
            'search_default_state': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_customer_id': self.partner_id.id,
            'default_nombre': self.name,
            'default_user_id': self.user_id.id,
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id)]
        quotations = self.mapped('bim_order_ids')
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('base_bim_2.view_form_bim_project').id, 'form')]
            action['res_id'] = quotations.id
        return action

    @api.depends('bim_order_ids.state_id', 'bim_order_ids.currency_id', 'bim_order_ids.company_id')
    def _compute_project_data(self):
        for lead in self:
            total = 0.0
            quotation_cnt = 0
            company_currency = lead.company_currency or self.env.company.currency_id
            for order in lead.bim_order_ids:
                quotation_cnt += 1
                total += order.currency_id._convert(
                    order.balance, company_currency, order.company_id,
                    order.date_ini or fields.Date.today())
            lead.bim_order_amount_total = total
            lead.bim_quotation_count = quotation_cnt