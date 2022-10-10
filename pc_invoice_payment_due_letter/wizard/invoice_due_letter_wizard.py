# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class InvoiceDueLetterWizard(models.TransientModel):
    _name = 'x.invoice.due.letter.wizard'
    _description = 'Invoice due letter wizard'

    response = fields.Selection([('1', 'Invoice date'), ('2', 'Maturity date'), ('3', 'Invoice')], string='Search by')
    date_invoice_from = fields.Date('Invoice date from', help='Invoice date from', copy=False)
    date_invoice_to = fields.Date('Invoice date to', help='Invoice date to', copy=False)
    date_maturity_from = fields.Date('Invoice maturity from', help='Maturity date from', copy=False)
    date_maturity_to = fields.Date('Invoice maturity to', help='Maturity date to', copy=False)
    invoice_from = fields.Many2one('account.move', 'Invoice from', help='Invoice from', copy=False)
    invoice_to = fields.Many2one('account.move', 'Invoice to', help='Invoice to', copy=False)


    @api.constrains('date_invoice_from', 'date_invoice_to', 'date_maturity_from', 'date_maturity_from')
    def _check_dates(self):
        if self.response in ('1', '2') and (self.date_invoice_from and self.date_invoice_to and self.date_invoice_from > self.date_invoice_to) \
            or (self.date_maturity_from and self.date_maturity_to and self.date_maturity_from > self.date_maturity_to):
            raise ValidationError(_('Second date must be later than first!.'))
        #if self.date_maturity_from and self.date_maturity_to and self.date_maturity_from > self.date_maturity_to:
        #    raise ValidationError(_('Second date must be later than first!.'))

    @api.constrains('invoice_from', 'invoice_to')
    def _check_invoice_ids(self):
        if self.response == '3' and self.invoice_from and self.invoice_to and self.invoice_from.id > self.invoice_to.id:
            raise ValidationError(_('Second invoice must be later than first!.'))


    #Método para obtener las facturas impagadas desde el wizard.
    def action_get_invoice_due(self):
        date_from = self.date_invoice_from if self.response == 1 else self.date_maturity_from
        date_to = self.date_invoice_to if self.response == 1 else self.date_maturity_to


        if self.response in ('1', '2'):
            #Facturas con fechas o fechas de vencimiento entre las indicadas en el wizard.
            invoices_due_ids = self.env['account.move'].search([('state', '=', 'posted'), ('payment_state', 'in', ['not_paid', 'partial']), \
                ('date_maturity', '>=', date_from), ('date_maturity', '<=', date_to) ])
        else:
            #Facturas con ID's entre factura desde/hasta.
            invoices_due_ids = self.env['account.move'].search([('state', '=', 'posted'), ('payment_state', 'in', ['not_paid', 'partial']), \
                ('id', '>=', invoice_from.id), ('id', '<=', invoice_to.id) ])

        if invoices_due_ids:
            #_logger.info('\ninvoices_due_ids:%s\n', invoices_due_ids)
            raise ValidationError(_('Invoice Due Ids!!'))

        partner_ids = invoices_due_ids.mapped('partner_id')
        for partner in partner_ids:
            invoice_ids = invoices_due_ids.search([('partner_id', '=', partner)])
            #_logger.info('\n*** invoices_by_partner - partner:%s - invoices:%s ***\n', partner.name, invoice_ids.mapped('name'))


    #Método para obtener las facturas impagadas desde el wizard.
    def open_invoice_due(self):

        #_logger.info('\n*** open_invoice_due - INICIO **\n')
        tree_view_id = self.env.ref('account.view_out_invoice_tree').id
        form_view_id = self.env.ref('account.view_move_form').id

        if self.response in ('1', '2'):
            field_date = 'invoice_date' if self.response == '1' else 'invoice_date_due'
            #date_from = self.date_invoice_from.strftime('%d-%m-%Y') if self.response == '1' else self.date_maturity_from.strftime('%d-%m-%Y')
            #date_to = self.date_invoice_to.strftime('%d-%m-%Y') if self.response == '1' else self.date_maturity_to.strftime('%d-%m-%Y')
            date_from = self.date_invoice_from.strftime('%Y-%m-%d') if self.response == '1' else self.date_maturity_from.strftime('%Y-%m-%d')
            date_to = self.date_invoice_to.strftime('%Y-%m-%d') if self.response == '1' else self.date_maturity_to.strftime('%Y-%m-%d')

            domain = [('move_type', '=', 'out_invoice'), ('x_has_move_due', '=', True), (field_date, '>=', date_from), (field_date, '<=', date_to)]
        else:
            domain = [('move_type', '=', 'out_invoice'), ('x_has_move_due', '=', True), ('id', '>=', self.invoice_from.id), ('id', '<=', self.invoice_to.id)]
        #domain = [('move_type', '=', 'out_invoice'), (field_date, '&gt;=', date_from), (field_date, '<=', date_to), ('x_has_move_due', '=', True)]
        #_logger.info('\n*** open_invoice_due - response:%s - DOMAIN: %s **\n', self.response, domain)
        #domain=[('state', '=', 'posted'), ('payment_state', 'in', ('not_paid', 'partial')), \
        #        ('invoice_date_due', '&gt;', date_from.strftime('%Y-%m-%d')), \
        #        ('invoice_date_due', '&lt;', date_to.strftime('%Y-%m-%d'))]

        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'domain': domain,
            'context': self.env.context,
            'target': 'current',
            #'context': dict(self.env.context, to_date=self.inventory_datetime),
        }
        #_logger.info('\n*** open_invoice_due - FIN **\n action:%s\n', action)
        return action

