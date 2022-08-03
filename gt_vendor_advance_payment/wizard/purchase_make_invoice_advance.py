from itertools import accumulate
import time
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

class PurchaseMakeInvoiceAdvance(models.TransientModel):
	_name = 'purchase.advance.payment.inv'
	_description = 'purchase advance payment invoice '

	@api.model
	def _count(self):
	    return len(self._context.get('active_ids', []))

	@api.model
	def _default_product_id(self):
	    product_id = self.env['ir.config_parameter'].sudo().get_param('purchase.default_prepayment_product_id')
	    return self.env['product.product'].browse(int(product_id)).exists()

	@api.model
	def _default_deposit_account_id(self):
	    return self._default_product_id().property_account_income_id

	@api.model
	def _default_deposit_taxes_id(self):
	    return self._default_product_id().taxes_id

	@api.model
	def _default_currency_id(self):
		if self._context.get('active_model') == 'sale.order' and self._context.get('active_id', False):
			sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
			return sale_order.currency_id

	@api.model
	def _default_has_down_payment(self):
		if self._context.get('active_model') == 'purchase.order' and self._context.get('active_id', False):
			purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))
			return purchase_order.order_line.filtered(
				lambda purchase_order_line: purchase_order_line.is_downpayment
				)
		return False

	advance_payment_method = fields.Selection([
        ('delivered', 'Regular invoice'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)')
        ], string='Create Invoice', default='delivered', required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing, \
        according to their invoicing policy (based on ordered or delivered quantity).")
	product_id = fields.Many2one('product.product', string='Down Payment Product', domain=[('type', '=', 'service')],
	    default=_default_product_id)
	count = fields.Integer(default=_count, string='# of Orders')
	amount = fields.Float('Down Payment Amount(Percentage)', digits=dp.get_precision('Account'), help="The amount to be invoiced in advance, taxes excluded.")
	deposit_account_id = fields.Many2one("account.account", string="Expense Account", domain=[('deprecated', '=', False)],
	    help="Account used for deposits", default=_default_deposit_account_id)
	currency_id = fields.Many2one('res.currency', string='Currency', default=_default_currency_id)
	deposit_taxes_id = fields.Many2many("account.tax", string="Customer Taxes", help="Taxes used for deposits", default=_default_deposit_taxes_id)
	fixed_amount = fields.Monetary('Down Payment Amount(Fixed)', help="The fixed amount to be invoiced in advance, taxes excluded.")
	has_down_payments = fields.Boolean('Has down payments', default=_default_has_down_payment, readonly=True)
	deduct_down_payments = fields.Boolean('Deduct down payments', default=True)
	acumulate = fields.Float(string="Accumulate")

	@api.onchange('advance_payment_method')
	def onchange_advance_payment_method(self):
	    if self.advance_payment_method == 'percentage':
	        return {'value': {'amount': 0}}
	    return {}

	@api.model
	def default_get(self, vals):
		res = super(PurchaseMakeInvoiceAdvance,self).default_get(vals)
		product_ids = self.env['ir.default'].get('res.config.settings', 'prepayment_account_id')
		res.update({'deposit_account_id':product_ids})
		return res

	def _create_invoice(self, order, po_line, amount):
		if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
			raise UserError(_('The value of the down payment amount must be positive.'))
		if self.advance_payment_method == 'percentage':
			amount = order.amount_untaxed * self.amount / 100
			name = _("Down payment of %s%%") % (self.amount,)
		else:
			amount = self.fixed_amount
			name = _('Down Payment')
		invoice_vals = {
		'move_type': 'in_invoice',
		'invoice_origin': order.name,
		'invoice_user_id': order.user_id.id,
		'narration': order.notes,
		'partner_id': order.partner_id.id,#order.partner_invoice_id.id,
		'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
		'partner_shipping_id': order.dest_address_id.id,#order.partner_shipping_id.id,
		'currency_id': order.currency_id.id,#order.pricelist_id.currency_id.id,
		'payment_reference': order.client_order_ref,
		'invoice_payment_term_id': order.payment_term_id.id,
		'team_id': order.team_id.id,
		'invoice_line_ids': [(0, 0, {
			'name': name,
			'price_unit': amount,
			'quantity': 1.0,
			'product_id': self.product_id.id,
			'purchase_line_id': [(6, 0, [po_line.id])],
			'analytic_tag_ids': [(6, 0, po_line.analytic_tag_ids.ids)],
			'analytic_account_id': po_line.account_analytic_id.id or False,
			'tax_ids': [(6, 0, self.deposit_taxes_id.ids)],
			})],
		}
		if order.fiscal_position_id:
			invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
		invoice = self.env['account.move'].create(invoice_vals)
		invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
		return invoice

	def create_invoices(self):
		purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))

		if self.advance_payment_method == 'delivered':
			purchase_orders._create_invoices(final=self.deduct_down_payments)
			purchase_orders.is_regular_invoice = True
		else:
			if not self.product_id:
				vals = self._prepare_deposit_product()
				self.product_id = self.env['product.product'].create(vals)
				self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
			purchase_line_obj = self.env['purchase.order.line']
			for order in purchase_orders:
				if self.advance_payment_method == 'percentage':
					amount = order.amount_untaxed * self.amount / 100
					for line in order.order_line:
						if line.product_qty == 0.0 and line.price_subtotal == 0.0 and line.qty_received == 0.0:
							line.dowm_payment = True
				else:
					amount = self.fixed_amount
				if self.product_id.invoice_policy != 'order':
					raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
				if self.product_id.type != 'service':
					raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
				taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
				if order.fiscal_position_id and taxes:
					tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
				else:
					tax_ids = taxes.ids
				context = {'lang': order.partner_id.lang}
				analytic_tag_ids = []
				for line in order.order_line:
					analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

				po_line = purchase_line_obj.create({
					'name': _('Down Payment: %s') % (time.strftime('%m %Y'),),
					'price_unit': amount,
					'product_qty':0.0,
					'order_id': order.id,
					'product_uom': self.product_id.uom_id.id,
					'product_id': self.product_id.id,
					'analytic_tag_ids': analytic_tag_ids,
					'taxes_id': [(6, 0, tax_ids)],
					'is_downpayment': True,
					'qty_invoiced':-1,
					#'date_planned':line.date_planned,
					'dowm_payment':True,
					})
				del context
				po_invoice_id = self._create_invoice(order, po_line, amount)
				purchase_orders.hide_invoice = False
				if po_invoice_id:
					purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
					inv_ids = self.env['account.move'].search([('invoice_origin', '=',purchase_orders.name)]).ids
					list_view_id = self.env.ref('account.view_invoice_tree').id
					form_view_id = self.env.ref('account.view_move_form').id
					result = {
					       "type": "ir.actions.act_window",
					       "res_model": "account.move",
					       "views": [[list_view_id, "tree"], [form_view_id, "form"]],
					       "domain": [("id", "in", inv_ids)],
					       "name":"Inv"
					}
					if len(inv_ids) == 1:
					   result['views'] = [(form_view_id, 'form')]
					   result['res_id'] = inv_ids[0]
				return result

	def _prepare_deposit_product(self):
		return {
		    'name': 'Down payment',
		    'type': 'service',
		    'invoice_policy': 'order',
		    'property_account_income_id': self.deposit_account_id.id,
		    'taxes_id': [(6, 0, self.deposit_taxes_id.ids)],
		}
