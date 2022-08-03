# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        res = super()._create_returns()
        picking = self.env['stock.picking'].browse(res[0])
        if picking:
            picking.returned = True
        return res

class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'
    ###### FIELDS ######
    code = fields.Char('Short Name', required=True, help="Short name used to identify your warehouse")

class StockMove(models.Model):
    _inherit = 'stock.move'
    ###### FIELDS ######
    supplier_id = fields.Many2one('res.partner')

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    ###### FIELDS ######
    supplier_id = fields.Many2one('res.partner', related="move_id.supplier_id")

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    bim_requisition_id = fields.Many2one('bim.purchase.requisition','Requisition')
    bim_project_id = fields.Many2one('bim.project','Project', domain="[('company_id','=',company_id)]")
    bim_budget_id = fields.Many2one('bim.budget', 'Budget', domain="[('project_id','=',bim_project_id)]")
    bim_concept_id = fields.Many2one('bim.concepts', 'Concept', domain="[('budget_id','=',bim_budget_id),('type','=','departure')]")
    bim_space_id = fields.Many2one('bim.budget.space','Space', domain="[('budget_id','=',bim_budget_id)]")
    bim_object_id = fields.Many2one('bim.object','BIM Object', domain="[('project_id','=',bim_project_id)]")
    bim_worder_id = fields.Many2one('bim.work.order', 'Work Order')
    check_to_rewrite = fields.Boolean('Overwrite destination')
    invoice_guide_number = fields.Char('Invoice Guide No.')
    include_for_bim = fields.Boolean(default=lambda self: self.env.company.include_picking_cost)
    returned = fields.Boolean(default=False)

    @api.onchange('bim_requisition_id')
    def bim_req_change(self):
        new_lines = self.env['stock.move']
        self.move_lines = False
        req = self.bim_requisition_id
        for line in req.product_ids:
            if not line.done    :
                new_line = new_lines.new({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.despachado,
                    'date': req.date_begin,
                    'forecast_expected_date': req.date_prevista and req.date_prevista or datetime.today(),
                    'state': 'draft',
                    'price_unit': line.product_id.standard_price,
                    'picking_type_id': self.picking_type_id.id,
                    'origin': req.name,
                    'location_id': self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_src_id.id or False,
                    'location_dest_id': req.project_id.stock_location_id and req.project_id.stock_location_id.id or False,
                    'warehouse_id': self.picking_type_id and self.picking_type_id.warehouse_id.id or False,
                })
                new_lines += new_line
        self.move_lines += new_lines
        return {}

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        super(StockPicking, self).onchange_picking_type()
        if self.bim_requisition_id:
            self.location_dest_id = self.bim_requisition_id.project_id.stock_location_id \
                and self.bim_requisition_id.project_id.stock_location_id.id or False

    def action_force_assign(self):
        for picking in self:
            for move in picking.move_ids_without_package:
                if move.product_uom_qty != move.quantity_done:
                    move.quantity_done = move.product_uom_qty
        return True

    @api.onchange('bim_project_id')
    def _onchange_bim_project_id(self):
        for record in self:
            record.bim_budget_id = False
            record.bim_concept_id = False

    @api.onchange('bim_budget_id')
    def _onchange_bim_budget_id_id(self):
        for record in self:
            record.bim_concept_id = False

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    resource_type = fields.Selection(related='product_tmpl_id.resource_type', string="Resource Type", store=True)
