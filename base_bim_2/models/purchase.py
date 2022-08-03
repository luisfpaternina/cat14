# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    bim_requisition_id = fields.Many2one('bim.purchase.requisition', 'Requisition')
    part_id = fields.Many2one('bim.part', 'Report')
    project_id = fields.Many2one('bim.project', 'Project', tracking=True, domain="[('company_id','=',company_id)]")
    budget_id = fields.Many2one('bim.budget', 'Budjet', ondelete="restrict", domain="[('project_id','=',project_id)]")
    concept_id = fields.Many2one('bim.concepts', 'Concept', ondelete="restrict", domain="[('budget_id','=',budget_id),('type','=','departure')]")

    def action_view_invoice(self, moves=False):
        result = super(PurchaseOrder, self).action_view_invoice(moves)
        for record in self:
            project = record.env['bim.purchase.requisition'].search([('name', '=', record.origin)])
            default_project_id = project.project_id.id
            result.update({
                            'context': {'default_move_type': 'in_invoice',
                                        'default_project_id': default_project_id
                                        }
            })
        return result

    def button_confirm(self):
        result = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.bim_requisition_id:
                project = order.bim_requisition_id.project_id
                for pick in order.picking_ids:
                    pick.bim_project_id = project.id
                    if not pick.bim_requisition_id:
                        pick.bim_requisition_id = order.bim_requisition_id.id
        if self.project_id:
            history_obj = self.env['bim.product.purchase']
            for line in self.order_line:
                vals = {
                    'template_id': line.product_id.product_tmpl_id.id,
                    'product_id': line.product_id.id,
                    'date': date.today(),
                    'project_id': self.project_id.id,
                    'purchase_price': line.price_unit,
                    'purchase_id': self.id,
                    'supplier_id': self.partner_id.id,
                    'quantity': line.product_qty
                }
                history_obj.create(vals)
        return result

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            used_project_warehouse = self.company_id.use_project_warehouse
            if used_project_warehouse and self.project_id.warehouse_id:
                picking_type_id = self.env['stock.picking.type'].search([('warehouse_id','=',self.project_id.warehouse_id.id),('code','=','incoming')],limit=1)
                if picking_type_id:
                    self.picking_type_id = picking_type_id

    def _prepare_invoice(self):
        values = super()._prepare_invoice()
        values.update({
            'project_id': self.project_id.id or False,
            'budget_id': self.budget_id.id or False,
            'concept_id': self.concept_id.id or False,
        })
        return values


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    bim_req_line_id = fields.Many2one('product.list', 'Requisition Line')

    def _prepare_account_move_line(self, move=False):
        values = super()._prepare_account_move_line(move)
        values.update({
            'analytic_account_id': self.order_id.project_id.analytic_id.id or False
        })
        return values
