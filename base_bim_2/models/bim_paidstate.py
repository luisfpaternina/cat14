# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class bim_paidstate(models.Model):
    _description = "Payment Status"
    _name = 'bim.paidstate'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    user_id = fields.Many2one('res.users', string='Responsible', tracking=True, default=lambda self: self.env.user)
    name = fields.Char('Name', required=True, copy=False,
        readonly=True, index=True, default=lambda self: 'New')
    project_id = fields.Many2one('bim.project', 'Project',
        states={'draft': [('readonly', False)]}, required=True, readonly=True, domain="[('company_id','=',company_id)]",
        change_default=True, index=True, ondelete="restrict")
    amount = fields.Monetary('Balance', compute='_amount_compute')
    amount_total = fields.Monetary('Balance', compute='_amount_compute')
    progress = fields.Float('% Advance', help="Advance percentage", compute='compute_progress', store=True)
    date = fields.Date(string='Date', required=True,
        readonly=True, index=True, states={'draft': [('readonly', False)]},
        copy=False, default=fields.Datetime.now)
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, default=lambda r: r.env.user.company_id.currency_id,
        tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, ondelete='restrict')
    maintenance_id = fields.Many2one('bim.maintenance', string='Maintenance project', readonly=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company, required=True)
    lines_ids = fields.One2many('bim.paidstate.line', 'paidstate_id', string='Lines')
    object_lines_ids = fields.One2many('bim.paidstate.object.line', 'paidstate_id', string='Object Lines')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('validated', 'Validated'),
         ('invoiced', 'Invoiced'),
         ('cancel', 'Canceled')],
        'Status', readonly=True, copy=False,
        index=True, tracking=True, default='draft')
    apply_retention = fields.Boolean(string='Apply retention', default=True)
    paidstate_retention = fields.Float(string='Warranty Retention', compute='compute_retention', store=True)
    paidstate_company_retention = fields.Float(string='% Project Retention', related='project_id.retention')
    paidstate_notes = fields.Text()
    type = fields.Selection([('manual','Manual'),('certification','By Certification')], default='manual', required=True)
    invoice_debit_credit = fields.Boolean(default=lambda self: self.env.company.invoice_debit_credit)

    def action_paid_state_cancel(self):
        if self.state != 'invoiced':
            self.state = 'cancel'
        if self.state == 'invoiced':
            if self.invoice_id.state == 'cancel':
                self.state = 'cancel'
            else:
                action = self.env.ref('base_bim_2.bim_paidstate_wizard_cancel_action').sudo().read()[0]
                return action

    @api.depends('amount')
    def compute_progress(self):
        for record in self:
            paidstate_ids = self.env['bim.paidstate'].search([('project_id','=',record.project_id.id)])
            amount_total = 0
            for paidstate in paidstate_ids:
                amount_total += paidstate.amount
            record.progress = amount_total / record.project_id.balance * 100 if record.project_id.balance > 0 else 0

    @api.depends('lines_ids')
    def compute_retention(self):
        for record in self:
            if record.apply_retention:
                record.paidstate_retention = -0.01 * record.amount * record.project_id.retention
            else:
                record.paidstate_retention

    @api.depends('lines_ids')
    def _amount_compute(self):
        for record in self:
            record.amount = sum(line.amount for line in record.lines_ids)
            record.amount_total = sum(line.amount_total for line in record.lines_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.paidstate') or "New"
        return super(bim_paidstate, self).create(vals)

    def action_validate(self):
        if not self.lines_ids and not self.object_lines_ids:
            raise UserError(_("There are not lines to Validate"))
        self.write({'state': 'validated'})

    def unlink(self):
        if self.state == 'invoiced':
            raise UserError(_("It is not possible to delete Invoiced Paid State Record"))
        for record in self:
            for line in record.lines_ids:
                line.budget_id.balance_certified_residual += line.price_unit
        return super().unlink()

    def action_invoice(self):
        invoice_obj = self.env['account.move']
        record = self
        #Si el estado de pago proviene de un mantenimiento entonces toma el Product configurado en Ajustes para mantenimiento
        if not record.maintenance_id:
            if record.project_id.paidstate_product:
                product = record.project_id.paidstate_product
            else:
                product = self.env.user.company_id.paidstate_product
        else:
            product = self.env.user.company_id.paidstate_product_mant
        if record.project_id.retention_product:
            retention_product = record.project_id.retention_product
        else:
            retention_product = self.env.user.company_id.retention_product
        if not record.project_id.customer_id:
            raise UserError(_('A client must be added to the project before invoicing.'))
        if not product:
            raise UserError(_('Define a product to invoice the Payment Status directly at the Work. You can also enter BIM / Configuration / Settings and configure a default one'))
        if not retention_product:
            raise UserError(_(
                'Define a product to invoice the withholding in the Payment Statements directly in the Work. You can also enter BIM / Configuration / Settings and configure a default one'))
        income_account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
        retention_account = retention_product.property_account_income_id or retention_product.categ_id.property_account_income_categ_id
        if not retention_account:
            raise UserError(_('There is no income account in the withholding product or in its category.'))
        if not income_account:
            raise UserError(_('There is no income account in the product or in its category'))
        journal = self.env.user.company_id.journal_id.id
        if not journal:
            raise UserError(_('You have not set up a Sales Journal'))
        ###################################################

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': record.project_id.invoice_address_id.id if record.project_id.invoice_address_id else record.project_id.customer_id.id,
            'partner_shipping_id': record.project_id.customer_id.id,
            'journal_id': journal,
            'currency_id': self.env.user.company_id.currency_id.id,
            'invoice_date': record.date,
            'invoice_user_id': self.env.user.id,
            'invoice_line_ids': [],
            'narration': record.paidstate_notes
        }
        if record.type == 'manual':
            for line in record.object_lines_ids:
                invoice_vals['invoice_line_ids'].append(
                    (0, 0,
                     {
                         'name': '%s - %s' % (record.name, record.project_id.nombre[0:40]),
                         'sequence': 1,
                         'account_id': income_account.id,
                         'analytic_account_id': record.project_id.analytic_id and record.project_id.analytic_id.id or False,
                         'price_unit': line.amount,
                         'quantity': 1,
                         'product_uom_id': product.uom_id.id,
                         'product_id': product.id,
                         'tax_ids': [(6, 0, product.taxes_id.ids)],
                     }))
        else:
            for line in record.lines_ids:
                 invoice_vals['invoice_line_ids'].append(
                    (0, 0,
                     {
                        'name': '%s - %s'%(record.name, record.project_id.nombre[0:40]),
                        'sequence': 1,
                        'account_id': income_account.id,
                        'analytic_account_id': record.project_id.analytic_id and record.project_id.analytic_id.id or False,
                        'price_unit': line.amount if not record.invoice_debit_credit else line.amount_total,
                         'quantity': line.quantity,
                        'product_uom_id': product.uom_id.id,
                        'product_id': product.id,
                        'tax_ids': [(6, 0, product.taxes_id.ids)],
                      }))
        # Agregamos el Product DE RETENCION
        if self.apply_retention:
            invoice_vals['invoice_line_ids'].append(
                (0, 0,
                 {
                     'name': '%s - %s - %s' % (record.name, record.project_id.nombre[0:40], str(record.project_id.retention) + '%'),
                     'sequence': 1,
                     'account_id': retention_account.id,
                     'analytic_account_id': record.project_id.analytic_id and record.project_id.analytic_id.id or False,
                     'price_unit': record.paidstate_retention,
                     'quantity': 1,
                     'product_uom_id': product.uom_id.id,
                     'product_id': retention_product.id,
                     'tax_ids': [(6, 0, retention_product.taxes_id.ids)],
                 }))
        ###################################################
        invoice = invoice_obj.create(invoice_vals)
        record.invoice_id = invoice.id
        record.project_id.write({'invoice_ids': [(4, invoice.id)]})
        if record.maintenance_id:
            record.maintenance_id.invoice_id = invoice.id
            record.maintenance_id.write({'invoice_ids': [(4, invoice.id)]})
        record.write({'state': 'invoiced'})
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        res = self.env.ref('account.view_move_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = invoice.id
        return result

    @api.onchange('lines_ids')
    def onchange_lines_ids(self):
        for record in self:
            record.amount = sum(x.amount for x in record.lines_ids)



class BimPaidstateLine(models.Model):
    _description = "Comparative indicators"
    _name = 'bim.paidstate.line'

    name = fields.Char('Description', required=True)
    quantity = fields.Integer('Quantity', default=1)
    percent = fields.Float('%', help="Percentage given by the real value between the estimated value", store=True)
    price_unit = fields.Float("Price")
    certification_factor = fields.Float()
    amount = fields.Float('Balance', compute='_amount_compute', store=True)
    amount_total = fields.Float('Balance', compute='_amount_compute', store=True)
    paidstate_id = fields.Many2one('bim.paidstate', 'Payment State', ondelete="cascade")
    project_id = fields.Many2one('bim.project', 'Project', related='paidstate_id.project_id')
    budget_id = fields.Many2one('bim.budget', 'Budget')
    is_loaded = fields.Boolean(default=False)

    @api.onchange('budget_id')
    def onchange_budget_id(self):
        budget_list = []
        if self.paidstate_id:
            budget_list.append(self.paidstate_id.project_id.id)
        return {'domain': {'budget_id': [('project_id','in',budget_list)]}}

    @api.onchange('budget_id')
    def onchange_name(self):
        name_list = []
        if self.budget_id:
            name_list.append(self.budget_id.name)
        self.name = name_list and '-'.join(name_list) or ''

    @api.depends('quantity','price_unit','certification_factor')
    def _amount_compute(self):
        for record in self:
            record.amount = record.quantity * record.price_unit
            record.amount_total = record.amount * record.certification_factor

    def unlink(self):
        for record in self:
            record.budget_id.balance_certified_residual += record.price_unit
        return super().unlink()


class BimPaidstateObjectLine(models.Model):
    _description = "Bim .Paid state Object Line"
    _name = 'bim.paidstate.object.line'

    paidstate_id = fields.Many2one('bim.paidstate', 'Payment State', ondelete="cascade")
    project_id = fields.Many2one('bim.project', related='paidstate_id.project_id')
    percent = fields.Float('%')
    amount = fields.Float("Amount", required=True)
    object_id = fields.Many2one('bim.object', domain="[('project_id','=',project_id)]", required=True)
    is_loaded = fields.Boolean(default=False)





