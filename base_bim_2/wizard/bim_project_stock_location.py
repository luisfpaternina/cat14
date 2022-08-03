# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError,ValidationError


class BimProjectStockLocation(models.TransientModel):
    _name = 'bim.project.stock.location'
    _description = "Bim project stock location wizard"

    @api.model
    def default_get(self, fields):
        res = super(BimProjectStockLocation, self).default_get(fields)
        context = self._context
        active_id = context.get('active_id', False)
        model = context.get('active_model', False)
        value = self.env[model].browse(active_id)
        lines = []

        if model == 'bim.concepts':
            project = value.budget_id.project_id
            res['project_id'] = project.id
            res['budget_id'] = value.budget_id.id
            res['concept_id'] = active_id
        else:
            project = value
            location = project.stock_location_id
            self.env.cr.execute('''
                select product_id,location_id,sum(quantity) as qty
                from stock_quant
                where location_id = %d
                group by product_id,location_id
                order by product_id''' % (location.id))
            result = self.env.cr.dictfetchall()
            product_obj = self.env['product.product']
            for row in result:
                template = product_obj.browse(row['product_id']).product_tmpl_id
                supplier = False
                history = template.bim_purchase_ids.filtered_domain([('product_id','=',row['product_id']),('template_id','=',template.id),('project_id','=',project.id)])
                if history:
                    supplier = history[0].supplier_id.id
                lines.append((0, 0, {'product_id': row['product_id'], 'qty': row['qty'], 'location_id': row['location_id'],'supplier_id': supplier}))
            res['project_id'] = project.id
            res['bim_stock_lines'] = lines
        return res

    # ========== Wizard fields ===========
    project_id = fields.Many2one('bim.project', string='Project')
    budget_id = fields.Many2one('bim.budget', 'Budjet', domain="[('project_id','=',project_id)]")
    concept_id = fields.Many2one('bim.concepts', 'Concept', domain="[('budget_id','=',budget_id),('type','=','departure')]")
    space_id = fields.Many2one('bim.budget.space', string='Space')
    object_id = fields.Many2one('bim.object', string='Project Object')
    type = fields.Selection([
        #('wait', 'SELECCIONE UNA OPCION:'),
        ('in_stock', 'Only outbound of products in this Budget Item'),
        ('prj_stock', 'Only outbound of products in Project Location'),
        ('out_stock', 'Any product')],
        'Type')
    bim_stock_lines = fields.One2many(
        'bim.project.stock.location.lines',
        'wizard_id', string='Lines')
    include_for_bim = fields.Boolean(default=lambda self: self.env.company.include_picking_cost)
    # =====================================

    @api.onchange('space_id')
    def onchange_space(self):
        if self.space_id:
            if self.space_id.object_id:
                self.object_id = self.space_id.object_id

    @api.onchange('budget_id')
    def onchange_budget_id_id(self):
        if self.budget_id and self.concept_id.budget_id and self.concept_id.budget_id != self.budget_id:
            self.concept_id = False

    @api.onchange('type')
    def _onchange_lines(self):
        if self.type:
            project = self.project_id
            location = project.stock_location_id
            StockQ = self.env['stock.quant']
            if self.concept_id and not self.concept_id.child_ids:
                raise ValidationError(_('There are no Resources in the selected Budget Item'))

            if self.type == 'in_stock':
                lines = []
                res_ids = []
                childs = self.concept_id.child_ids
                res_ids = self.recursive_search(childs)

                for product in self.env['product.product'].browse(res_ids):
                    qty = StockQ._get_available_quantity(product,location)
                    lines.append((0, 0, {'product_id': product.id, 'qty': qty, 'location_id': location.id}))

                if self.bim_stock_lines:
                    self.bim_stock_lines = [(5, 0, 0)]
                self.bim_stock_lines = lines

            elif self.type == 'prj_stock':
                lines = []
                res_ids = []
                childs = self.concept_id.child_ids
                res_ids = self.recursive_search(childs)

                for product in self.env['product.product'].browse(res_ids):
                    qty = StockQ._get_available_quantity(product,location)
                    if qty > 0:
                        lines.append((0, 0, {'product_id': product.id, 'qty': qty, 'location_id': location.id}))
                if self.bim_stock_lines:
                    self.bim_stock_lines = [(5, 0, 0)]
                self.bim_stock_lines = lines
            else:
                self.bim_stock_lines = [(5, 0, 0)]

    def recursive_search(self, child_ids):
        domain = ['material'] # filtro
        res_product = []
        for record in child_ids:
            if record.product_id and record.type in domain and record.product_id.type != 'service':
                res_product.append(record.product_id.id)
                if record.child_ids:
                    self.recursive_search(record.child_ids)
        return res_product

    def action_load(self):
        project = self.project_id
        company = self.env.company
        picking_type_obj = self.env['stock.picking.type']
        location_id = project.stock_location_id.id
        location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')])
        move_lines = []

        if not project.stock_location_id:
            raise ValidationError(_('There is not Stock Location configured in this Project'))

        for i in self.bim_stock_lines:
            if not i.qty_add:
                continue
            move_lines.append([0, False, {
                'product_id': i.product_id.id,
                'product_uom_qty': i.qty_add,
                'supplier_id': i.supplier_id.id,
                'purchase_id': i.purchase_id.id if i.purchase_id else False,
                'product_uom': i.product_id.uom_id.id,
                'price_unit': i.product_id.lst_price,
                'name': i.product_id.name_get()[0][-1]}])

        picking_type = picking_type_obj.search([
            ('default_location_src_id', '=', location_id),
            ('code', '=', 'outgoing')],limit=1)
        if not picking_type:
            warehouse = self.env['stock.warehouse'].search([('partner_id','=',company.partner_id.id)],limit=1)
            picking_type = picking_type_obj.search([('warehouse_id', '=', warehouse.id),('code', '=', 'outgoing')],limit=1)

        dicc = {}
        dicc.update({
            'picking_type_id': picking_type.id,
            'location_id': location_id,
            'move_lines': move_lines,
            'include_for_bim': self.include_for_bim,
            'company_id': self.env.user.company_id.id,
            'origin': project.name,
            'partner_id': project.customer_id.id,
            'location_dest_id': location_dest_id.id,
            'bim_concept_id': self.concept_id and self.concept_id.id or False,
            'bim_budget_id': self.budget_id and self.budget_id.id or False,
            'bim_project_id': project.id,
            'bim_space_id': self.space_id and self.space_id.id or False,
            'bim_object_id': self.object_id and self.object_id.id or False,
            'move_type': 'direct',
        })
        picking = self.env['stock.picking'].create(dicc)
        #self.concept_id.picking_ids = [(4,picking.id,None)]
        if company.validate_stock:
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        picking.action_force_assign()
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            picking._action_done()

        return {'type': 'ir.actions.act_window_close'}

class BimProjectStockLocationLines(models.TransientModel):
    _name = 'bim.project.stock.location.lines'
    _description = "Bim project stock location lines wizard"

    wizard_id = fields.Many2one('bim.project.stock.location', 'Wizard')
    product_id = fields.Many2one('product.product', 'Product')
    location_id = fields.Many2one('stock.location', 'Location')
    qty = fields.Float('Available')
    qty_add = fields.Float('Quantity to move', required=True, default=0.0)
    supplier_id = fields.Many2one('res.partner')
    purchase_id = fields.Many2one('purchase.order',domain="[('partner_id','=',supplier_id),('company_id','=',company_id)]")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company,
                                 readonly=True)
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id and self.product_id.type == 'service':
            warning = {
                'title': _('Warning!'),
                'message': _(u'Product of type Service can not be selected!'),
            }
            self.product_id = False
            return {'warning': warning}

        if self.product_id and self.wizard_id.type == 'out_stock':
            self.qty = self.product_id.qty_available




