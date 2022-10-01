# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderTemplateInherit(models.Model):
    _inherit = 'sale.order.template'

    sale_type_id = fields.Many2one(
        'sale.order.type',
        string="Sale type")
    type_contract = fields.Selection([
        ('normal','Normal'),
        ('risk','All risk')],string="Type of contract",tracking=True)
    gadgets_contract_type_id = fields.Many2one('stock.gadgets.contract.type')

    """
    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Quotation Template',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    """