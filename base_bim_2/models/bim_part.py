# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError,ValidationError

class BimPart(models.Model):
    _description = "BIM Parts"
    _name = 'bim.part'
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.part') or "New"
        return super(BimPart, self).create(vals)

    name = fields.Char('Code', default="New")
    obs = fields.Text('Notes', translate=True)
    date = fields.Date(string='Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    budget_id = fields.Many2one('bim.budget', string='Budjet', domain="[('project_id','=',project_id)]")
    concept_id = fields.Many2one('bim.concepts', 'Concept', ondelete="cascade")
    project_id = fields.Many2one('bim.project', string='Project', domain="[('company_id','=',company_id)]")
    space_id = fields.Many2one('bim.budget.space', string='Space')
    partner_id = fields.Many2one('res.partner', string='Supplier', tracking=True)
    user_id = fields.Many2one('res.users', string='Responsable', tracking=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company, readonly=True)
    lines_ids = fields.One2many('bim.part.line', 'part_id', 'Lines')
    purchase_ids = fields.One2many('purchase.order', 'part_id', 'Purchases')
    purchase_count = fields.Integer('N° Purchases', compute="_compute_purchases_count")
    part_total = fields.Float(compute='_compute_part_total')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('validated', 'Validated'),
         ('cancel', 'Cancelled')],
        'Status', readonly=True, copy=False,
        tracking=True, default='draft')
    type = fields.Selection(selection=[
        ('per_document', 'Per Document'),
        ('per_lines', 'Per Líne')],
        string='Type', required=True,
        copy=False, tracking=True, default='per_document')
    elements_readonly = fields.Boolean(default=False)

    @api.onchange('partner_id','type')
    def onchange_partner_for_type(self):
        if self.partner_id and self.type == 'per_document':
            for line in self.lines_ids:
                line.partner_id = self.partner_id.id
        elif self.type == 'per_document' and not self.partner_id:
            for line in self.lines_ids:
                line.partner_id = False

    @api.onchange('project_id')
    def onchange_project(self):
        if self.project_id and not self.elements_readonly:
            self.budget_id = False
            self.concept_id = False

    @api.onchange('budget_id')
    def onchange_budget_id(self):
        if self.budget_id and not self.elements_readonly:
            self.concept_id = False


    def action_validate(self):
        self.write({'state': 'validated'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def create_purchase_order(self):
        self.ensure_one()
        suppliers = []
        add = False
        if self.type == 'per_lines':
            for line in self.lines_ids:
                supp = {
                    'id': line.partner_id.id
                }
                if suppliers:
                    for supplier in suppliers:
                        if supplier['id'] == supp['id']:
                            add = False
                            break
                        else:
                            add = True
                else:
                    add = True
                if add:
                    suppliers.append(supp)
        else:
            supp = {
                    'id': self.partner_id.id
                }
            suppliers.append(supp)
        context = self._context
        PurchaseOrd = self.env['purchase.order']
        purchases = []

        for supplier in suppliers:
            purchase_lines = []
            order = PurchaseOrd.create({
                    'partner_id': supplier['id'],
                    'origin': self.name,
                    'date_order': fields.Datetime.now(),
                    'part_id': self.id,
                    'project_id': self.project_id.id if self.project_id else False,
                    'budget_id': self.budget_id.id if self.budget_id else False,
                    'concept_id': self.concept_id.id if self.concept_id else False,
                })
            if self.type == 'per_lines':
                for line in self.lines_ids.filtered(lambda l: l.partner_id.id == supplier['id']):
                    purchase_lines.append((0,0,{
                        'name': line.name.name,
                        'product_id': line.name.id,
                        'product_uom': line.product_uom.id,
                        'product_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'taxes_id': [(6, 0, line.name.supplier_taxes_id.ids)],
                        'date_planned': self.date,
                        'account_analytic_id': self.project_id.analytic_id.id,
                    }))
            else:
                for line in self.lines_ids:
                    purchase_lines.append((0,0,{
                        'name': line.name.name,
                        'product_id': line.name.id,
                        'product_uom': line.product_uom.id,
                        'product_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'taxes_id': [(6, 0, line.name.supplier_taxes_id.ids)],
                        'date_planned': self.date,
                        'account_analytic_id': self.project_id.analytic_id.id,
                    }))
            order.order_line = purchase_lines
            self.write({'purchase_ids': [(4, order.id, None)]})
        return True

    @api.depends('purchase_ids')
    def _compute_purchases_count(self):
        for part in self:
            part.purchase_count = len(part.purchase_ids)

    @api.depends('lines_ids','lines_ids.price_subtotal')
    def _compute_part_total(self):
        for part in self:
            part.part_total = sum(line.price_subtotal for line in part.lines_ids)

    def action_view_purchase_order(self):
        purchases = self.mapped('purchase_ids')
        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        if len(purchases) > 0:
            action['domain'] = [('id', 'in', purchases.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

class BimPartLine(models.Model):
    _description = "Parts of Project"
    _name = 'bim.part.line'

    partner_id = fields.Many2one('res.partner', string='Supplier')
    name = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True)
    description = fields.Char('Description')
    product_uom_qty = fields.Float(string='Quantity', digits='BIM qty', required=True)
    product_uom = fields.Many2one('uom.uom', string='UdM', domain="[('category_id', '=', product_uom_category_id)]")
    price_unit = fields.Float(string='Price', required=True, digits='BIM price')
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal')
    part_id = fields.Many2one('bim.part', 'Project Report')
    product_uom_category_id = fields.Many2one(related='name.uom_id.category_id')
    resource_type = fields.Selection(
        [('M', 'Material'),
         ('H', 'Labor'),
         ('Q', 'Equipment'),
         ('S', 'Sub-Contract'),
         ('HR', 'Tool'),
         ('A', 'Administrative'),
         ('F', 'Function')],
        'Resourse Type', default='M')
    filter_type = fields.Char(compute='_compute_parent_type')
    type = fields.Selection(related='part_id.type')

    @api.onchange('name')
    def onchange_product(self):
        if self.name and self.name.type != 'service':
            warning = {
                'title': _('Warning!'),
                'message': _(u'You cannot select a Product of a Type different than Service!'),
            }
            self.name = False
            return {'warning': warning}

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_amount(self):
        for record in self:
            record.price_subtotal = record.price_unit * record.product_uom_qty

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self._compute_parent_type()
        if self.partner_id:
            if self.part_id.partner_id != self.partner_id and self.part_id.type == 'per_document':
                raise ValidationError(_('Different Supplier can not be selected'))
        if self.type == 'per_document':
            self.partner_id = self.part_id.partner_id.id

    @api.onchange('name')
    def _onchange_name(self):
        self.product_uom = self.name.uom_id.id
        self.resource_type = self.name.resource_type
        self.price_unit = self.name.standard_price

    @api.depends('part_id.type','part_id.partner_id','part_id.lines_ids')
    def _compute_parent_type(self):
        for rec in self:
            if rec.part_id.type == 'per_document':
                rec.filter_type = 'doc'
            else:
                rec.filter_type = 'line'



