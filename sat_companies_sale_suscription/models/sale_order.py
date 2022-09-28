# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

class SaleOrderTemplateInherit(models.Model):
    _inherit = 'sale.order'
    
    gadgets_contract_type_id = fields.Many2one(
        'stock.gadgets.contract.type')
    acc_number = fields.Char(
        string="Acc number")
    check_contract_type = fields.Boolean(
        compute="_compute_check_contract_type")
    
    exclude_months = fields.Boolean(
        'Exlude Months')

    subscription_month_ids = fields.Many2many(
        'sale.subscription.month')


    def _compute_check_contract_type(self):
        for record in self:
            if record.sale_type_id.is_maintenance:
                record.check_contract_type = True
            else:
                record.check_contract_type = False

    '''
    @api.onchange('partner_id')
    def _get_partner_acc_account(self):
        partner_obj = self.env['res.partner'].search([('name', '=', self.partner_id.name)],limit=1)
        for p in partner_obj.bank_ids:
            if p.is_default:
                self.acc_number = p.acc_number
    '''

    @api.onchange('partner_id')
    def _get_partner_acc_account(self):
        if self.partner_id.bank_ids:
            acc_default = self.partner_id.bank_ids.filtered(lambda r: r.is_default == True)
            if acc_default:
                self.acc_number = acc_default[0].acc_number #Por si hubiese más de 1 marcada por defecto (en teoría no se podría, pero por importaciones).
            else:
                self.acc_number = self.partner_id.bank_ids[0].acc_number
        else:
            self.acc_number = ''


    @api.onchange('sale_type_id')
    def domain_saletype_udn(self):
        for record in self:
            if record.sale_type_id:
                return {'domain': {'sale_order_template_id': [('sale_type_id', '=', record.sale_type_id.id)]}}
            else:
                return {'domain': {'sale_order_template_id': []}}

    def create_subscriptions(self):
        res = super(SaleOrderTemplateInherit, self).create_subscriptions()
        res = []
        for order in self:
            if order.sale_type_id.is_maintenance == True:
                if order.product_id.subscription_template_id:
                    to_create = {}
                    # to_create[order.product_id.subscription_template_id] = order.order_line
                    to_create[order.product_id.subscription_template_id] = order.order_line.filtered(lambda r: r.display_type == False)
                    #to_create.append(order.product_id.subscription_template_id)
                    #to_create.append(order.order_line)
                    # create a subscription for each template with all the necessary lines
                    if order.order_line:
                        for template in to_create:
                            values = order._prepare_subscription_data(template)
                            values.update({
                                'product_id': order.product_id.id,
                                'sale_type_id': order.sale_type_id.id,
                                'task_user_id': order.task_user_id.id,
                                'gadgest_contract_type_id': order.gadgets_contract_type_id.id,
                                'date_begin': order.date_begin,
                                'date_end': order.date_end,
                                'subscription_month_ids': order.subscription_month_ids.ids,
                                'exclude_months': order.exclude_months

                            })
                            values['recurring_invoice_line_ids'] = to_create[template]._prepare_subscription_line_data()
                            subscription = self.env['sale.subscription'].sudo().create(values)
                            subscription.onchange_date_start()
                            res.append(subscription.id)
                            to_create[template].write({'subscription_id': subscription.id})
                            subscription.message_post_with_view(
                                'mail.message_origin_link', values={'self': subscription, 'origin': order},
                                subtype_id=self.env.ref('mail.mt_note').id, author_id=self.env.user.partner_id.id
                            )
                            project_task = self.env['project.task'].search([('sale_order_id.id','=',order.id)])

                            for task in project_task:
                                self.env['sale.subscription.log'].sudo().create({
                                    'subscription_id': subscription.id,
                                    'event_date': fields.Date.context_today(self),
                                    'event_type': '0_creation',
                                    'amount_signed': subscription.recurring_monthly,
                                    'recurring_monthly': subscription.recurring_monthly,
                                    'currency_id': subscription.currency_id.id,
                                    'category': subscription.stage_category,
                                    'user_id': order.user_id.id,
                                    'team_id': order.team_id.id,
                                    'project_task_id': task.id or False
                                })

        return res
