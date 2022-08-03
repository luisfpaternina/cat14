# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging


class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_id = fields.Many2one(
        'sale.subscription',
        string="Subscription")
    product_id = fields.Many2one(
        'product.template',
        'Gadgets')
    gadgets_contract_type_id = fields.Many2one(
        'stock.gadgets.contract.type')
    task_user_id = fields.Many2one(
        'res.users')
    sale_type_id = fields.Many2one(
        'sale.order.type')
    date_begin = fields.Datetime(
        string = 'Date asigned')
    date_end = fields.Datetime(
        string = 'Date End asingned')
    gadget_contract_type = fields.Many2one(
        'stock.gadgets.contract.type',
        string="Contract type")
    is_potential_client = fields.Boolean(
        string="Is a potential client",
        tracking=True,
        related="partner_id.is_potential_client")
    check_product = fields.Boolean(
        compute='compute_check_product')
    check_contract_type = fields.Boolean(
        compute="_compute_check_contract_type")
    rae = fields.Char(
        string="R.A.E",
        related="product_id.rae")
    subscription_template_id = fields.Many2one(
        'sale.subscription.template',
        string="Subscription template",
        related="product_id.subscription_template_id")
    udn_type_id = fields.Many2one(
        'project.task.categ.udn',
        string="Udn")


    @api.onchange('sale_type_id', 'product_id')
    def domain_udns(self):
        for record in self:
            if record.sale_type_id:
                return {'domain': {'udn_type_id': [('ot_type_id', '=', record.sale_type_id.id)]}}
            else:
                return {'domain': {'udn_type_id': []}}

    @api.depends('sale_type_id')
    def _compute_check_contract_type(self):
        for record in self:
            if record.sale_type_id.code == '01':
                record.check_contract_type = True
            else:
                record.check_contract_type = False

    @api.depends('product_id')
    def compute_check_product(self):
        for record in self:
            if record.product_id:
                record.check_product=True
            else:
                record.check_product=False

    @api.onchange('product_id')
    def onchange_check_product(self):
        for record in self:
            if record.product_id.employee_notice_id.user_id:
                record.task_user_id = record.product_id.employee_notice_id.user_id
            sale_type = record.product_id.subscription_template_id.sale_type_id
            gadgets_contract = record.product_id.subscription_template_id.gadgets_contract_type_id
            record.sale_type_id = sale_type
            record.gadgets_contract_type_id = gadgets_contract
