# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
import logging
_logger = logging.getLogger(__name__)



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    x_is_out_overdue = fields.Boolean('Is out overdue', default=False, compute='_compute_x_is_out_overdue', store=True, copy=False)

    '''
    unreconciled_aml_ids = fields.One2many('account.move.line', 'partner_id',
                                           domain=[('reconciled', '=', False),
                                                   ('account_id.deprecated', '=', False),
                                                   ('account_id.internal_type', '=', 'receivable'),
                                                   ('move_id.state', '=', 'posted')])

            record.unpaid_invoices = self.env['account.move'].search([
                ('company_id', '=', self.env.company.id),
                ('commercial_partner_id', '=', record.id),
                ('state', '=', 'posted'),
                ('payment_state', 'not in', ('paid', 'in_payment')),
                ('move_type', 'in', self.env['account.move'].get_sale_types())
            ]).filtered(lambda inv: not any(inv.line_ids.mapped('blocked')))
    '''

    #Calcula si el apunte está vencido (sólo se hace para facturas de venta). TO-DO. Hay que ejecutarlo también desde una planificada por el cambio de día.
    @api.depends('parent_state', 'move_id.payment_state', 'date_maturity', 'journal_id', 'reconciled')
    def _compute_x_is_out_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.x_is_out_overdue = (record.date_maturity != False) and (record.parent_state == 'posted') and (record.move_id.payment_state not in ('paid', 'in_payment', 'invoicing_legacy')) \
                and (record.date_maturity < today) and (record.journal_id.type == 'sale') #\
                #and (record.reconciled == False) #and (record.move_id.company_id == self.env.company.id)
            #TO-DO. Comprobar si es necesario comprobar el campo  "blocked"

    