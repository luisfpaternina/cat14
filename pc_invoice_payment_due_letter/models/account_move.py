# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
import base64
import logging
_logger = logging.getLogger(__name__)



class AccountMove(models.Model):
    _inherit = 'account.move'


    x_has_move_due = fields.Boolean('Has move due', default=False, compute='_compute_x_has_move_due', store=True, copy=False)
    x_has_aml_due = fields.Boolean('Has aml due', default=False, compute='_compute_x_has_aml_due', store=True, copy=False)
    x_sent_due_letter = fields.Boolean('Sent due letter notification', default=False, copy=False)
    x_last_sent_due_letter = fields.Datetime('Last sent due letter', help='Last due letter sent date', copy=False)


    #Calcula si la factura tiene alguno de sus vencimientos vencidos.
    @api.depends('state', 'payment_state', 'invoice_date', 'invoice_date_due', 'line_ids.date_maturity')
    def _compute_x_has_move_due(self):
        today = fields.Date.today()
        for record in self:
            lines = record.line_ids.search([('move_id', '=', record.id), ('reconciled', '=', False), ('journal_id.type', '=', 'sale'), ('parent_state', '=', 'posted'), \
                    ('move_id.payment_state', 'in', ['not_paid', 'partial']), ('date_maturity', '<', today)])
            record.x_has_move_due = len(lines) > 0

    #Calcula si la factura tiene alguno de sus vencimientos vencidos (con el campo de las líneas de apuntes contables)
    @api.depends('state', 'payment_state', 'invoice_date', 'invoice_date_due', 'line_ids.date_maturity', 'line_ids.x_is_out_overdue')
    def _compute_x_has_aml_due(self):
        for record in self:
            overdue_lines = record.line_ids.search_count([('move_id', '=', record.id), ('x_is_out_overdue', '=', True)])
            record.x_has_aml_due = overdue_lines > 0
            #_logger.info('\n*** has_aml_due - invoice:%s - overdue_lines:%s ***\n', record.name, overdue_lines)



    
    #Método para generar las cartas de impagados desde la vista Tree de Facturas. Se invoca desde una acción.
    def action_send_invoice_due_letter(self):
        InvoiceDue = self.env['x.invoice.payment.due']
        InvoiceDue.search([]).unlink()

        invoice_due_ids = self.browse(self._context.get('active_ids')).filtered('x_has_move_due')
        #if invoices_due_ids:
        #    _logger.info('\ninvoices_due_ids:%s\n', invoices_due_ids)
        #else: raise ValidationError(_('There is not invoices with overdue!'))
        template = self.env.ref('pc_invoice_payment_due_letter.mail_template_invoice_due_letter', raise_if_not_found=False)

        if not template:
            _logger.warning('Template "pc_invoice_payment_due_letter.mail_template_invoice_due_letter" was not found. Cannot send invoice due letters!!')
            return

        #_logger.info('\n*** action_send_invoice_due_letter - template:%s - invoices:%s ***\n', template.name, invoice_due_ids.mapped('name'))


        partner_ids = invoice_due_ids.mapped('partner_id') #Se obtienen los clientes para enviar sólo 1 carta por cliente.
        for partner in partner_ids:
            invoice_ids = invoice_due_ids.search([('id', 'in', invoice_due_ids.ids), ('partner_id', '=', partner.id)])
            invoice_line_ids = invoice_ids.mapped('line_ids').filtered('x_is_out_overdue') #Sólo para comprobar en el log si son las correctas.
            #_logger.info('\n*** send_mail invoice_ids:%s - line_ids:%s ***\n', invoice_ids, invoice_line_ids)
            _logger.info('\n*** invoices_by_partner - partner:%s - invoices:%s - line_ids:%s ***\n*** unpaid_invoices:%s\n unreconciled_aml_ids:%s  ***\n', \
                        partner.name, invoice_ids.mapped('name'), invoice_line_ids, partner.unpaid_invoices, partner.unreconciled_aml_ids)

            #Se insertan los registros en el modelo de impagados.
            record = InvoiceDue.create({
                'partner_id': partner.id,
                'partner_admin_id': invoice_ids[0].product_id.partner_admin_id.id, #Se asigna el administrador de la 1ª factura porque sólo se puede mostrar uno.
                'date': fields.Datetime.now(),
                'invoice_ids': [(6, 0, invoice_ids.ids)],
                #'amount': partner.id,
            })
            #_logger.info('\n*** InvoiceDue:%s ***\n', record)


            '''
            mail = template.send_mail(record.id)
            if mail:
                invoice_ids.write({
                    'x_sent_due_letter' : True,
                    'x_last_sent_due_letter' : fields.Datetime.now(),
                })
                _logger.info('\n*** Bucle partner:%s ENVIADO MAIL: %s ***\n', partner.id, mail)
            mail_id = self.env['mail.mail'].search([('id', '=', mail)])
            for invoice in invoice_ids:
                message=self.env['mail.message'].create({
                    'message_type': mail_id.message_type,
                    #'subtype_id': self.env.ref("mail.mt_comment").id,
                    'subject': mail_id.subject,
                    'body': mail_id.body_html,
                    'email_from': mail_id.email_from,
                    'partner_ids': mail_id.partner_ids.ids,
                    'attachment_ids': mail_id.attachment_ids.ids,
                    'model': 'account.move',
                    'res_id': invoice.id,
                    'author_id': 2, #Odoobot
                    'is_internal': True,
                })
            '''


        InvoiceDue.search([])._send_invoice_due_letter() #Método que genera y las cartas desde el modelo x.invoice.payment.due.

