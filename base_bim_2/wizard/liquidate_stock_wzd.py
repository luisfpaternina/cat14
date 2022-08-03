# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta

class LiquidateStockWzd(models.TransientModel):
    _name = "liquidate.stock.wzd"
    _description = 'Liquidate Stock WZD'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        context = self._context
        res['project_id'] = context['active_id']
        return res

    company_id = fields.Many2one('res.company',related='project_id.company_id')
    location_dest_id = fields.Many2one('stock.location', domain="[('company_id','=',company_id),('usage','=','internal')]", required=True)
    project_id = fields.Many2one('bim.project')

    def action_liquidate_stock(self):
        picking_lines = []
        for quant in self.project_id.stock_location_id.quant_ids:
            if quant.quantity > 0:
                line_vals = {
                    'product_id': quant.product_id.id,
                    'product_uom_qty': quant.quantity,
                    'product_uom': quant.product_id.uom_id.id,
                    'name': self.project_id.name
                }
                picking_lines.append((0, 0, line_vals))
        picking_type_id = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', self.project_id.warehouse_id.id), ('code', '=', 'internal')], limit=1)

        if len(picking_lines) > 0:
            vals = {
                'picking_type_id': picking_type_id.id,
                'date': datetime.now(),
                'origin': self.project_id.name,
                'location_dest_id': self.location_dest_id.id,
                'location_id': self.project_id.stock_location_id.id,
                'company_id': self.company_id.id,
                'move_ids_without_package': picking_lines
            }
            picking = self.env['stock.picking'].create(vals)
            picking.action_confirm()
            picking.action_assign()
            picking._action_done()
            for line in picking.move_ids_without_package:
                line.quantity_done = line.product_uom_qty
            picking.button_validate()
            self.project_id.message_post(body=_("All products from this Project were liquidated to another location: {} in transfer: {} by user: {}").format(self.location_dest_id.name,picking.name,self.env.user.name))
        else:
            raise UserError(_("There is not product to liquidate in this Project"))




    def action_liquidate_stock2(self):
        locations = self.lines_ids.mapped('location_id')
        transfer = False
        for location in locations:
            lines = self.lines_ids.filtered_domain([('location_id', '=', location.id)])
            picking_lines = []
            for line in lines:
                if line.stock_quantity > 0 and line.location_id:
                    quantity = line.product_uom_qty if line.stock_quantity >= line.product_uom_qty else line.stock_quantity
                    line_vals = {
                        'product_id': line.product_id.id,
                        'product_uom': line.stock_move_id.product_uom.id,
                        'product_uom_qty': quantity,
                        'reserved_availability': quantity,
                        'name': line.stock_move_id.name
                    }
                    picking_lines.append((0, 0, line_vals))
            if self.type == 'from' and self.picking_id.picking_type_code == 'outgoing':
                location_dest_id = self.picking_id.location_id
                location_id = location
            elif self.type == 'to' and self.picking_id.picking_type_code == 'outgoing':
                location_dest_id = location
                location_id = self.picking_id.location_id
            elif self.type == 'from' and self.picking_id.picking_type_code == 'incoming':
                location_dest_id = self.picking_id.location_dest_id
                location_id = location
            elif self.type == 'to' and self.picking_id.picking_type_code == 'incoming':
                location_dest_id = location
                location_id = self.picking_id.location_dest_id
            elif self.type == 'from' and self.picking_id.picking_type_code == 'internal':
                location_dest_id = self.picking_id.location_id
                location_id = location
            elif self.type == 'to' and self.picking_id.picking_type_code == 'internal':
                location_dest_id = location
                location_id = self.picking_id.location_dest_id

            if len(picking_lines) > 0:
                transfer = True
                vals = {
                    'picking_type_id': self.picking_id.picking_type_id.id,
                    'partner_id': self.picking_id.partner_id.id,
                    'user_id': self.picking_id.user_id.id,
                    'date': datetime.now(),
                    'origin': self.picking_id.name,
                    'location_dest_id': location_dest_id.id,
                    'location_id': location_id.id,
                    'company_id': self.company_id.id,
                    'moved_from': self.picking_id.id,
                    'move_ids_without_package': picking_lines
                }
                picking = self.env['stock.picking'].create(vals)
                picking.action_confirm()
                picking.action_assign()
                picking._action_done()
                for line in picking.move_ids_without_package:
                    line.quantity_done = line.product_uom_qty
                picking.button_validate()

                self.picking_id.message_post(
                    body=(_("Created Internal Product Transference from {} to {}")).format(location_id.name,
                                                                                           location_dest_id.name))
        if not transfer:
            raise UserError(_("There are not available products to transfer!"))
        if not locations:
            raise UserError(_("There are not selected locations for products!"))
