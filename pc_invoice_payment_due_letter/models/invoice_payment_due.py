# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
from datetime import date, timedelta
import logging
_logger = logging.getLogger(__name__)

class InvoicePaymentDue(models.Model):
    _name = 'x.invoice.payment.due'
    _description = 'Model invoice payment due'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, index=True)
    partner_admin_id = fields.Many2one('res.partner', string='Administrator')
    date = fields.Date('Date')#, default=fields.Date.today())
    invoice_ids = fields.Many2many('account.move', 'res_invoice_payment_due_account_move_rel', string="Invoice due")
    amount = fields.Float('Amount', compute='_compute_amount')


    #Calcula el importe total de cada registro.
    @api.depends('invoice_ids')
    def _compute_amount(self):
        today = fields.Date.today()
        for record in self:
            amount = 0
            for invoice in record.invoice_ids:
                lines = invoice.line_ids.search([('move_id', '=', invoice.id), ('reconciled', '=', False), ('journal_id.type', '=', 'sale'), ('parent_state', '=', 'posted'), \
                    ('move_id.payment_state', 'in', ['not_paid', 'partial']), ('date_maturity', '<', today)])
                amount += sum(lines.mapped('debit'))
            record.amount = amount


    #Método para enviar las cartas de impagados.
    def _send_invoice_due_letter(self):
        template = self.env.ref('pc_invoice_payment_due_letter.mail_template_invoice_due_letter', raise_if_not_found=False)
        custom_html = (_('<p style="color:red;">This message is a copy of the mail sent to customer</p></br>'))
        for record in self:
            #_logger.info('\n*** _send_invoice_due_letter- REGISTRO: %s ****\n', record.id)
            mail = template.send_mail(record.id)
            if mail:# or message:
                mail_id = self.env['mail.mail'].search([('id', '=', mail)])
                for invoice in record.invoice_ids:
                    invoice.write({
                        'x_sent_due_letter' : True,
                        'x_last_sent_due_letter' : datetime.datetime.now(),
                    })
                    message = self.env['mail.message'].create({
                        'message_type': mail_id.message_type, #'notification', #Se pone como notificación para evitar que se envíe por correo.
                        #'subtype_id': self.env.ref("mail.mt_comment").id,
                        'subject': mail_id.subject,
                        'body': custom_html + mail_id.body_html,
                        'email_from': mail_id.email_from,
                        'partner_ids': mail_id.partner_ids.ids,
                        'attachment_ids': mail_id.attachment_ids.ids,
                        'model': 'account.move',
                        'res_id': invoice.id,
                        'author_id': mail_id.author_id.id, #2, #Odoobot
                        'is_internal': True,
                    })
            _logger.info('\n*** _send_invoice_due_letter - record:%s - partner:%s - date:%s - invoices:%s - amount:%s ***\n', \
                        record.id, record.partner_id.name, record.date, record.invoice_ids.mapped('name'), record.amount)


    #Para guardar un histórico de los registros creados en el modelo de carta de impagados.
    @api.model
    def create(self, values):
        InvoiceDueHis = self.env['x.invoice.payment.due.history']
        res = super(InvoicePaymentDue, self).create(values)
        if res:
            record = InvoiceDueHis.create({
                'partner_id': res.partner_id.id,
                'partner_admin_id': res.partner_admin_id.id,
                'date':  res.date,
                'invoice_ids': res.invoice_ids.ids, #[(6, 0, res.invoice_ids.ids)], #(6, 0, [IDs])
                'amount': res.amount,
                'create_date': res.create_date,
                'create_uid': res.create_uid.id,
                'create_date': res.create_date,
            })
        else:
            raise UserWarning('Can not be create record on Invoice Payment Due model!')
        return res


#Modelo para guardar un histórico de los registros creados en el modelo de carta de impagados.
class InvoicePaymentDueHistory(models.Model):
    _name = 'x.invoice.payment.due.history'
    _description = 'Model invoice payment due history'

    partner_id = fields.Many2one('res.partner', string='Customer_', required=True, index=True, readonly=True)
    partner_admin_id = fields.Many2one('res.partner', string='Administrator_', readonly=True)
    date = fields.Date('Date_', readonly=True)
    invoice_ids = fields.Many2many('account.move', 'res_invoice_payment_due_history_account_move_rel', string="Invoices due", readonly=True)
    amount = fields.Float('Amount_', readonly=True)