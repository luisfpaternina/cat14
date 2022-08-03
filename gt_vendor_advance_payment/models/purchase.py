# -*- coding: utf-8 -*-
from itertools import groupby
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp
import logging

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    hide_invoice = fields.Boolean(string="Hide Invoice",default=False)
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    team_id = fields.Many2one(
        'crm.team', 'Purchases Team',
        change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    transaction_ids = fields.Many2many('payment.transaction', string='Transactions', copy=False, readonly=True)
    po_inv_count = fields.Integer(string="Purchase Invoice Count", compute='compute_purchase_inv_count')
    is_regular_invoice = fields.Boolean(string="Full payment",default=False,copy=False)
    partner_shipping_id = fields.Many2one('res.partner', string="Shipping partner")
    acumulate = fields.Float(string="Acumulate")


    def calculate_acumulate(self):
        invoice_obj = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        if invoice_obj:
            for inv in invoice_obj:
                self.acumulate = inv.amount_total

    def copy(self, default=None):
        duplicate_po = super(PurchaseOrder, self).copy(default=default)
        duplicate_po.hide_invoice = False
        return duplicate_po

    @api.depends('order_line.invoice_lines')
    def compute_purchase_inv_count(self):
        account_ids = self.env['account.move'].search([('invoice_origin', '=',self.name)]).ids
        self.po_inv_count = len(account_ids)
        return self.po_inv_count

    def button_confirm(self):
        if not self.order_line:
            raise UserError(_("Please select Product lines to confirm the order"))
        res=super(PurchaseOrder,self).button_confirm()
        return res

    def _prepare_invoice(self):
        
        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'in_invoice',
            'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_id.id,
            'fiscal_position_id': self.fiscal_position_id.id, #or self.partner_invoice_id.property_account_position_id.id,
            'invoice_origin': self.name,
            'origin_po': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.partner_ref,
            'company_id': self.company_id.id,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
        }
        return invoice_vals


    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:
            pending_section = None

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))

            if not invoice_vals['invoice_line_ids']:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('partner_id'), x.get('currency_id'))):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs),
                    'invoice_origin': ', '.join(origins),
                    'origin_po': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Manage 'final' parameter: transform out_invoice to out_refund if negative.
        out_invoice_vals_list = []
        refund_invoice_vals_list = []
        if final:
            for invoice_vals in invoice_vals_list:
                # for l in invoice_vals['invoice_line_ids']:
                if sum(l[2]['quantity'] * l[2]['price_unit'] for l in invoice_vals['invoice_line_ids']) < 0:
                    for l in invoice_vals['invoice_line_ids']:
                        l[2]['quantity'] = -l[2]['quantity']
                    invoice_vals['move_type'] = 'out_refund'
                    refund_invoice_vals_list.append(invoice_vals)
                else:
                    out_invoice_vals_list.append(invoice_vals)
        else:
            out_invoice_vals_list = invoice_vals_list

        # Create invoices.
        moves = self.env['account.move'].with_context(default_move_type='out_invoice').create(out_invoice_vals_list)
        moves += self.env['account.move'].with_context(default_move_type='out_refund').create(refund_invoice_vals_list)
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('purchase_line_id.order_id.name')},
                subtype_id=self.env.ref('mail.mt_note').id 
            )
        return moves

    def get_po_invoice_view_2(self):
        # purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        inv_ids = self.env['account.move'].search([('invoice_origin', '=',self.name)]).ids
        list_view_id = self.env.ref('account.view_invoice_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        result = {
               "type": "ir.actions.act_window",
               "res_model": "account.move",
               "views": [[list_view_id, "tree"], [form_view_id, "form"]],
               "domain": [("id", "in", inv_ids)],
               "name":"Invoice",
        }
        if len(inv_ids) == 1:
           result['views'] = [(form_view_id, 'form')]
           result['res_id'] = inv_ids[0]
        # self.invoice_count +=1 
        return result


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prepayment_account_id = fields.Many2one('account.account',"Prepayment Account",config_parameter='purchase.default_prepayment_product_id')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'prepayment_account_id', self.prepayment_account_id.id)
        
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(prepayment_account_id=IrDefault.get('res.config.settings', 'prepayment_account_id'))
        return res

class PurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'

    @api.depends('qty_invoiced', 'qty_received', 'product_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['purchase', 'done']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    qty_to_invoice = fields.Float(
        compute='_get_to_invoice_qty', string='To Invoice', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    dowm_payment = fields.Boolean(string="down payment",default=False)
    is_downpayment = fields.Boolean(
        string="Is a down payment", help="Down payments are made when creating invoices from a purchase order."
        " They are not copied when duplicating a purchase order.")
           
    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        values = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'purchase_line_id': [(4, self.id)],
        }
        return values

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        res = super(PurchaseOrderLine,self)._compute_qty_invoiced()
        for line in self:
            if line.dowm_payment == True:
                line.qty_invoiced = 1
