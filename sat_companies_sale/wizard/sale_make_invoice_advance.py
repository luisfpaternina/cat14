# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        for record in res:
            record.product_id = order.product_id
            record.task_user_id = order.task_user_id
            record.date_begin = order.date_begin
            record.date_end = order.date_end
            record.sale_type_id = order.sale_type_id
            record.gadgets_contract_type_id = order.gadgets_contract_type_id

        print('test')
        return res

