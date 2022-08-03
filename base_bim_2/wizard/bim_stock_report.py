# -*- coding: utf-8 -*-
import base64
import xlwt
import re
import io
import tempfile
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from xlwt import easyxf, Workbook
from datetime import datetime
from io import StringIO

class BimstockReportWizard(models.TransientModel):
    _name = "bim.stock.report.wizard"
    _description = "Wizard Report Budget Stock"

    @api.model
    def default_get(self, fields):
        res = super(BimstockReportWizard, self).default_get(fields)
        res['project_id'] = self._context.get('active_id', False)
        return res

    material = fields.Boolean(string="Materials",default=True)
    equipment = fields.Boolean(string="Equipment",default=True)
    labor = fields.Boolean(string="Labor",default=True)
    attendance = fields.Boolean(string="Attendance",default=True)
    invoice = fields.Boolean(string="Purchase Invoices",default=True)
    resource_all = fields.Boolean(default=True,string="All")
    date_beg = fields.Date('Date From', default=fields.Date.today)
    date_end = fields.Date('Date To')
    project_id = fields.Many2one('bim.project', "Budget", required=True)
    doc_type = fields.Selection([('csv', 'CSV'), ('xls', 'Excel')], string='Format', default='xls')
    display_type = fields.Selection([
        ('summary', 'Summarized'),
        ('detailed', 'Detailed'),
        ('range', 'Date Range')], string="Printing Type", default='summary',
        help="Report grouping form.")

    @api.onchange('equipment', 'material', 'labor')
    def onchange_resource(self):
        self.resource_all = True if (self.equipment and self.material and self.labor) else False

    @api.onchange('material')
    def onchange_material(self):
        self.invoice = self.material

    @api.onchange('labor')
    def onchange_labor(self):
        self.attendance = self.labor

    @api.onchange('resource_all')
    def onchange_resource_all(self):
        if not self.resource_all and (self.equipment and self.material and self.labor):
            self.equipment = self.material = self.labor = False
        elif self.resource_all:
            self.equipment = self.material = self.labor = True

    def get_space_quantity(self, concept, space):
        qty_space = 0
        if not concept.measuring_ids and concept.parent_id.type == 'departure':
            return self.get_space_quantity(concept.parent_id,space)
        qty_space = sum(m.amount_subtotal for m in concept.measuring_ids if m.space_id and m.space_id.id == space.id)
        return qty_space

    def recursive_quantity_space(self, resource, space, qty_space, qty=None):
        parent = resource.parent_id
        qty = qty is None and resource.quantity or qty

        if parent.type == 'departure':
            if not parent.measuring_ids:
                qty_partial = qty * parent.quantity
            else:
                qty_partial = qty
            return self.recursive_quantity_space(parent,space,qty_space,qty_partial)
        else:
            return qty * qty_space

    def recursive_quantity(self, resource, parent, qty=None):
        qty = qty is None and resource.quantity or qty
        if parent.type == 'departure':
            qty_partial = qty * parent.quantity
            return self.recursive_quantity(resource,parent.parent_id,qty_partial)
        else:
            return qty * parent.quantity

    def get_quantity(self,resource,concept,space):
        total_qty = 0
        if concept:
            records = concept.child_ids.filtered(lambda c: c.product_id.id == resource.id)
            if space:
                qty_space = self.get_space_quantity(concept,space)
                for rec in records:
                    if rec.quantity > 0:
                        total_qty += self.recursive_quantity_space(rec,space,qty_space,None)
            else:
                for rec in records:
                    if rec.quantity > 0:
                        total_qty += self.recursive_quantity(rec,rec.parent_id,None)
        return total_qty

    def get_budget_quantity_hours(self,concept,resource):
        total_qty = 0
        if concept:
            records = concept.child_ids.filtered(lambda c: c.product_id.id == resource.id)
            for rec in records:
                if rec.quantity > 0:
                    total_qty += self.recursive_quantity(rec,rec.parent_id,None)
        return total_qty

    def print_report(self):
        if self.display_type == 'detailed':
            print ('.....1....')
        elif self.display_type == 'range':
            print ('.....2....')
        else:
            self.print_xls()
        #action.update({'close_on_report_download': True})

    def get_stock_out(self,product,location,concept=False):
        quantity = 0
        if not concept:
            moves = self.env['stock.move'].search(['|',
                ('location_id', '=', location.id),
                ('location_dest_id', '=', location.id),
                ('product_id','=',product.id),
                ('picking_id.bim_concept_id','=',False)])
        else:
            moves = self.env['stock.move'].search(['|',
                ('location_id', '=', location.id),
                ('location_dest_id', '=', location.id),
                ('product_id','=',product.id),
                ('picking_id.bim_concept_id','=',concept.id)])
        if moves:
            for move in moves:
                if move.picking_id.include_for_bim:
                    if move.picking_id.returned:
                        quantity -= move.product_qty
                    else:
                        quantity += move.product_qty
        return quantity

    def get_part_out(self,product,res_type,concept):
        quantity = 0
        if concept:
            lines = self.env['bim.part.line'].search([
                ('name','=',product.id),
                ('resource_type','=',res_type),
                ('part_id.concept_id','=',concept.id)])
        if lines:
            quantity = sum(line.product_uom_qty for line in lines)
        return quantity

    def get_work_out(self,product,concept,lines):
        quantity = 0
        if lines:
            for line in lines:
                if line.type == 'budget_in':
                    if line.resource_id.product_id.id == product.id:
                        quantity += line.duration_real
                elif line.product_id == product.id:
                    quantity += line.duration_real
        return quantity

    def print_xls(self):
        self.ensure_one()
        project = self.project_id
        location = project.stock_location_id
        base_domain = [('bim_project_id','=',project.id),('include_for_bim','=',True),('state','=','done')]
        part_domain = [('project_id','=',project.id),('state','=','validated')]
        attendance_domain = [('project_id','=',project.id),('check_out','!=',False)]
        workorder_active = False
        invoice_domain = [('product_id','!=',False),('display_type','=',False),('move_id.move_type','in',['in_invoice','in_refund']),('move_id.state','=','posted'),('move_id.include_for_bim','=',True)]
        if project.analytic_id:
            invoice_domain.append(('analytic_account_id', '=', project.analytic_id.id))
        if self.display_type == 'summary':
            header = ["Código","Nombre","Inventario General","Inventario Ubicación","Presupuesto","Partida","Uom","Salidas","Coste","Importe"]
        elif self.display_type == 'range':
            base_domain.append(('date','>=',self.date_beg))
            base_domain.append(('date','<=',self.date_end))
            invoice_domain.append(('move_id.invoice_date','<=',self.date_end))
            invoice_domain.append(('move_id.invoice_date','>=',self.date_beg))
            part_domain.append(('date','>=',self.date_beg))
            part_domain.append(('date','<=',self.date_end))
            attendance_domain.append(('check_in','>=',self.date_beg))
            attendance_domain.append(('check_out','<=',self.date_end))
            header = ["Código","Nombre","Inventario General","Inventario Ubicación","Presupuesto","Partida","Uom","Salidas","Coste","Importe"]
        else:
            header = ["Código","Nombre","Movimiento/Parte","Presupuesto","Partida","Objeto de Obra","Espacio","Proveedor","Descripción","Fecha","Inventario General","Inventario Ubicación","Uom","Cantidad","Coste","Importe","Cantidad","Coste","Importe","Cantidad","Importe"]

        # Verificamos si esta activo Orden de Trabajo
        if 'bim_workorder' in self.env.registry._init_modules:
            workorder_active = True
            workorders = self.env['bim.workorder'].search([('project_id','=',project.id)])

        # Buscamos los picking de la Obra
        picking_obj = self.env['stock.picking']
        outgoing_domain = base_domain + [('picking_type_code','!=','incoming'),('returned','=',False)]
        pickings = picking_obj.search(outgoing_domain)
        incoming_domain = base_domain + [('picking_type_code','=','incoming'),('returned','=',True)]
        pickings += picking_obj.search(incoming_domain)

        #Buscamos las partidas
        departs = pickings.mapped('bim_concept_id')

        #Buscamos las Partes de la Obra
        parts = self.env['bim.part'].search(part_domain)
        dep_parts = parts.mapped('concept_id')

        # Buscamos asistencia de la Obra
        attendances = self.env['hr.attendance'].search(attendance_domain)
        employees = attendances.mapped('employee_id')

        # Buscamos las Facturas de Compra
        # invoices = self.env['account.move'].search(invoice_domain)
        invoice_lines = self.env['account.move.line'].search(invoice_domain)
        invoice_products = invoice_lines.mapped('product_id')
        invoice_concepts = invoice_lines.mapped('concept_id')
        invoice_records = invoice_lines.mapped('move_id')

        # Datos Para excel
        wb = Workbook(encoding='utf-8')
        ws = wb.add_sheet(_('Book'))
        Quants = self.env['stock.quant']
        style_title = easyxf('font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center')
        style_negative = easyxf('font: color red;')

        row = 0
        index = 0
        if self.display_type == 'detailed':
            ws.write_merge(row,row,13,15, _("BUDGET"),style_title)
            ws.write_merge(row,row,16,18, _("REAL EXECUTED"),style_title)
            ws.write_merge(row,row,19,20, _("DIFFERENCE"),style_title)
            row = row + 1

        for head in header:
            ws.write(row, index, head, style_title)
            index = index + 1

        row = row + 1

        # CALCULO DE LINEAS RESUMIDAS y RANGO
        if self.display_type in ['range','summary']:
            # (Partes)
            for concept in dep_parts:
                # Mano de Obra
                if self.labor:
                    product_ids = []
                    for part in parts.filtered(lambda pt: pt.concept_id.id == concept.id):
                        products = part.lines_ids.mapped('name')
                        for product in products.filtered(lambda p: p.resource_type == 'H'):
                            if not product.id in product_ids:
                                qty_location = Quants._get_available_quantity(product,location)
                                part_outs = self.get_part_out(product,'H',concept)
                                ws.write(row, 0, product.default_code or '')
                                ws.write(row, 1, product.display_name)
                                ws.write(row, 2, product.qty_available or 0)
                                ws.write(row, 3, qty_location or 0)
                                ws.write(row, 4, concept.budget_id.display_name)
                                ws.write(row, 5, concept.name)
                                ws.write(row, 6, product.uom_id.name)
                                ws.write(row, 7, part_outs)
                                ws.write(row, 8, product.standard_price)
                                ws.write(row, 9, part_outs*product.standard_price)
                                product_ids.append(product.id)
                                row += 1

                    # Mano de Obra desde Orden de TRabajo (Si esta instalado bim_workorder)
                    if workorder_active and workorders:
                        product_ids = []
                        bwor_obj = self.env['bim.workorder.resources']
                        for word in workorders:
                            for bwoc in word.concept_ids:
                                lines_with = bwor_obj.search([('workorder_concept_id','=',bwoc.id),('workorder_id','=',bwoc.workorder_id.id)])
                                lines_out = bwor_obj.search([('workorder_id','=',bwoc.workorder_id.id),('departure_id','=',bwoc.concept_id.id)])
                                lines = lines_with + lines_out
                                lines_mo = lines.filtered(lambda x:x.qty_execute > 0)

                                for line in lines_mo:
                                    product = line.resource_id.product_id if line.type == 'budget_in' else line.product_id
                                    if not product.id in product_ids:
                                        concept = line.concept_id if line.type == 'budget_in' else line.departure_id
                                        work_outs = self.get_work_out(product,concept,lines_mo)
                                        qty_location = Quants._get_available_quantity(product,location)
                                        ws.write(row, 0, product.default_code or '')
                                        ws.write(row, 1, product.display_name)
                                        ws.write(row, 2, product.qty_available or 0)
                                        ws.write(row, 3, qty_location or 0)
                                        ws.write(row, 4, concept and concept.budget_id.display_name or '')
                                        ws.write(row, 5, concept and concept.name or '')
                                        ws.write(row, 6, product.uom_id.name)
                                        ws.write(row, 7, work_outs)
                                        ws.write(row, 8, product.standard_price)
                                        ws.write(row, 9, work_outs*product.standard_price)
                                        product_ids.append(product.id)
                                        row += 1
                # Equipos
                if self.equipment:
                    product_ids = []
                    for part in parts.filtered(lambda pt: pt.concept_id.id == concept.id):
                        products = part.lines_ids.mapped('name')
                        for product in products.filtered(lambda p: p.resource_type == 'Q'):
                            if not product.id in product_ids:
                                qty_location = Quants._get_available_quantity(product,location)
                                part_outs = self.get_part_out(product,'Q',concept)
                                ws.write(row, 0, product.default_code or '')
                                ws.write(row, 1, product.display_name)
                                ws.write(row, 2, product.qty_available or 0)
                                ws.write(row, 3, qty_location or 0)
                                ws.write(row, 4, concept.budget_id.display_name)
                                ws.write(row, 5, concept.name)
                                ws.write(row, 6, product.uom_id.name)
                                ws.write(row, 7, part_outs)
                                ws.write(row, 8, product.standard_price)
                                ws.write(row, 9, part_outs*product.standard_price)
                                product_ids.append(product.id)
                                row += 1

            if self.resource_all:
                for balance in self.project_id.opening_balance_ids:
                    ws.write(row, 0, balance.name)
                    ws.write(row, 1, _("Opening Balance"))
                    ws.write(row, 2, '')
                    ws.write(row, 3, '')
                    ws.write(row, 4, balance.budget_id.display_name)
                    ws.write(row, 5, balance.concept_id.name if balance.concept_id else '')
                    ws.write(row, 6, '')
                    ws.write(row, 7, '')
                    ws.write(row, 8, '')
                    ws.write(row, 9, balance.amount)
                    row += 1

            # Materiales (Picking)
            if self.material:
                for concept in departs:
                    product_ids = []
                    for pick in pickings.filtered(lambda sp: sp.bim_concept_id.id == concept.id):
                        products = pick.move_lines.mapped('product_id')
                        for product in products:
                            if not product.id in product_ids:
                                quantity_done = self.get_stock_out(product, location, concept)
                                qty_location = Quants._get_available_quantity(product,location)
                                ws.write(row, 0, product.default_code or '')
                                ws.write(row, 1, product.display_name)
                                ws.write(row, 2, product.qty_available or 0)
                                ws.write(row, 3, qty_location or 0)
                                ws.write(row, 4, concept.budget_id.display_name)
                                ws.write(row, 5, concept.name)
                                ws.write(row, 6, product.uom_id.name)
                                ws.write(row, 7, quantity_done)
                                ws.write(row, 8, product.standard_price)
                                ws.write(row, 9, quantity_done * product.standard_price)
                                product_ids.append(product.id)
                                row += 1
                product_ids = []
                for pick in pickings.filtered(lambda sp: not sp.bim_concept_id):
                    for product in pick.move_lines.mapped('product_id'):
                        if not product.id in product_ids:
                            qty_location = Quants._get_available_quantity(product,location)
                            quantity_done = self.get_stock_out(product, location, concept)
                            ws.write(row, 0, product.default_code or '')
                            ws.write(row, 1, product.display_name)
                            ws.write(row, 2, product.qty_available or 0)
                            ws.write(row, 3, qty_location or 0)
                            ws.write(row, 4, '')
                            ws.write(row, 5, '')
                            ws.write(row, 6, product.uom_id.name)
                            ws.write(row, 7, quantity_done)
                            ws.write(row, 8, product.standard_price)
                            ws.write(row, 9, quantity_done * product.standard_price)
                            product_ids.append(product.id)
                            row += 1
            # aqui va asistencia resumida
            if self.attendance:
                for employee in employees:
                    employee_attendances = attendances.filtered_domain([('employee_id','=',employee.id)])
                    concepts = employee_attendances.mapped('concept_id')
                    for concept in concepts:
                        total_hours = 0
                        total_cost = 0
                        for attendance in employee_attendances.filtered_domain([('concept_id','=',concept.id)]):
                            total_hours += attendance.worked_hours
                            total_cost += attendance.attendance_cost
                        ws.write(row, 0, employee.bim_resource_id.default_code if employee.bim_resource_id else '')
                        ws.write(row, 1, employee.bim_resource_id.display_name if employee.bim_resource_id else employee.name )
                        ws.write(row, 2, '')
                        ws.write(row, 3, '')
                        ws.write(row, 4, '')
                        ws.write(row, 5, concept.name)
                        ws.write(row, 6, employee.bim_resource_id.uom_id.name if employee.bim_resource_id else '')
                        ws.write(row, 7, round(total_hours,2))
                        ws.write(row, 8, round(total_cost/total_hours,2) if total_hours > 0 else 0)
                        ws.write(row, 9, round(total_cost,2))
                        row += 1
                    total_hours = 0
                    total_cost = 0
                    for attendance in employee_attendances.filtered_domain([('concept_id', '=', False)]):
                        total_hours += attendance.worked_hours
                        total_cost += attendance.attendance_cost
                    ws.write(row, 0, employee.bim_resource_id.default_code if employee.bim_resource_id else '')
                    ws.write(row, 1,
                             employee.bim_resource_id.display_name if employee.bim_resource_id else employee.name)
                    ws.write(row, 2, '')
                    ws.write(row, 3, '')
                    ws.write(row, 4, '')
                    ws.write(row, 5, '')
                    ws.write(row, 6, employee.bim_resource_id.uom_id.name if employee.bim_resource_id else '')
                    ws.write(row, 7, round(total_hours, 2))
                    ws.write(row, 8, round(total_cost / total_hours, 2) if total_hours > 0 else 0)
                    ws.write(row, 9, round(total_cost, 2))
                    row += 1
            if self.invoice:
                for product in invoice_products:
                    qty_location = Quants._get_available_quantity(product, location)
                    for concept in invoice_concepts:
                        budget = concept.budget_id if concept.budget_id else False
                        product_invoiced_qty = 0
                        product_invoiced_price_total = 0
                        for line in invoice_lines.filtered_domain(
                                [('product_id', '=', product.id), ('concept_id', '=', concept.id)]):
                            factor = 1
                            if line.move_id.move_type == 'in_refund':
                                factor = -1
                            if self.env.company.include_vat_in_indicators:
                                product_invoiced_price_total += line.price_total * factor
                            else:
                                product_invoiced_price_total += line.price_subtotal * factor
                            product_invoiced_qty += line.quantity * factor

                        ws.write(row, 0, product.default_code or '')
                        ws.write(row, 1, product.display_name or '')
                        ws.write(row, 2, product.qty_available or 0)
                        ws.write(row, 3, qty_location)
                        ws.write(row, 4, budget.display_name if budget else '')
                        ws.write(row, 5, concept.name)
                        ws.write(row, 6, product.uom_id.name or '')
                        ws.write(row, 7, round(product_invoiced_qty, 2))
                        ws.write(row, 8, round(product_invoiced_price_total / product_invoiced_qty, 2) if product_invoiced_qty > 0 else 0)
                        ws.write(row, 9, round(product_invoiced_price_total, 2))
                        row += 1

                        product_invoiced_qty = 0
                        product_invoiced_price_total = 0
                        without_concept = False
                        for line in invoice_lines.filtered_domain(
                                [('product_id', '=', product.id), ('concept_id', '=', False)]):
                            factor = 1
                            without_concept = True
                            if line.move_id.move_type == 'in_refund':
                                factor = -1
                            if self.env.company.include_vat_in_indicators:
                                product_invoiced_price_total += line.price_total * factor
                            else:
                                product_invoiced_price_total += line.price_total * factor
                            product_invoiced_qty += line.quantity * factor

                        if without_concept:
                            ws.write(row, 0, product.default_code or '')
                            ws.write(row, 1, product.display_name or '')
                            ws.write(row, 2, product.qty_available or 0)
                            ws.write(row, 3, qty_location)
                            ws.write(row, 4, '')
                            ws.write(row, 5, '')
                            ws.write(row, 6, product.uom_id.name or '')
                            ws.write(row, 7, round(product_invoiced_qty, 2))
                            ws.write(row, 8, round(product_invoiced_price_total / product_invoiced_qty,
                                                   2) if product_invoiced_qty > 0 else 0)
                            ws.write(row, 9, round(product_invoiced_price_total, 2))
                            row += 1

                    # .Exportacion
        # CALCULO DE LINEAS DETALLADAS
        else:
            #Materiales (Picking)
            if self.material:
                for pick in pickings:
                    if pick.returned:
                        direction = -1
                    else:
                        direction = 1
                    for move in pick.move_lines:
                        qty_location = Quants._get_available_quantity(move.product_id,location)
                        budget = pick.bim_concept_id and pick.bim_concept_id.budget_id or False
                        departure = pick.bim_concept_id and pick.bim_concept_id or False
                        coste_real = move.product_cost
                        if workorder_active:
                            if not budget:
                                budget = move.workorder_departure_id and move.workorder_departure_id.budget_id or False
                            if not departure:
                                departure = move.workorder_departure_id and move.workorder_departure_id or False
                            if move.workorder_departure_id:
                                coste_real = move.price_unit

                        qty_budget = self.get_quantity(move.product_id,departure,pick.bim_space_id)
                        quantity_dif = qty_budget-move.product_uom_qty
                        amount_dif = (qty_budget*move.product_id.standard_price)-(move.product_uom_qty*move.product_id.standard_price)
                        supplier = ''
                        if move.supplier_id:
                            supplier = move.supplier_id.display_name
                        else:
                            if move.product_id.product_tmpl_id.bim_purchase_ids:
                                history = move.product_id.product_tmpl_id.bim_purchase_ids.filtered_domain([('project_id','=',project.id),('product_id','=',move.product_id.id)])
                                if history:
                                    supplier = history[0].supplier_id.display_name
                            elif move.product_id.seller_ids:
                                supplier = move.product_id.seller_ids[0].name.display_name
                        ws.write(row, 0, move.product_id.default_code or '')
                        ws.write(row, 1, move.product_id.display_name)
                        ws.write(row, 2, move.reference)
                        ws.write(row, 3, budget and budget.display_name or '')
                        ws.write(row, 4, departure and departure.name or '')
                        ws.write(row, 5, pick.bim_object_id and pick.bim_object_id.desc or '')
                        ws.write(row, 6, pick.bim_space_id and pick.bim_space_id.name or '')
                        ws.write(row, 7, supplier)
                        ws.write(row, 8, pick.note and pick.note or '')
                        ws.write(row, 9, datetime.strftime(move.date,'%Y-%m-%d'))
                        ws.write(row, 10, move.product_id.qty_available or 0)
                        ws.write(row, 11, qty_location or 0)
                        ws.write(row, 12, move.product_id.uom_id.name)
                        ws.write(row, 13, qty_budget)                                #Presupuesto
                        ws.write(row, 14, move.product_id.standard_price)            #Presupuesto
                        ws.write(row, 15, qty_budget*move.product_id.standard_price) #Presupuesto
                        ws.write(row, 16, move.product_uom_qty * direction)             #Ejecutado
                        ws.write(row, 17, coste_real)                       #Ejecutado
                        ws.write(row, 18, move.product_uom_qty*coste_real * direction)  #Ejecutado
                        if quantity_dif < 0:
                            ws.write(row, 19, quantity_dif,style_negative)
                        else:
                            ws.write(row, 19, quantity_dif)

                        if amount_dif < 0:
                            ws.write(row, 20, amount_dif,style_negative)
                        else:
                            ws.write(row, 20, amount_dif)
                        row += 1

            #  Mano de Obra
            if self.labor:
                for part in parts:
                    for line in part.lines_ids:
                        if line.resource_type == 'H':
                            product = line.name
                            qty_location = Quants._get_available_quantity(product,location)
                            qty_budget = self.get_quantity(product,part.concept_id,part.space_id)
                            quantity_dif = qty_budget-line.product_uom_qty
                            amount_dif = (qty_budget*product.standard_price)-line.price_subtotal
                            ws.write(row, 0, product.default_code or '')
                            ws.write(row, 1, product.display_name)
                            ws.write(row, 2, line.part_id.name)
                            ws.write(row, 3, part.concept_id and part.concept_id.budget_id.display_name or '')
                            ws.write(row, 4, part.concept_id and part.concept_id.name or '')
                            ws.write(row, 5, part.space_id.object_id and part.space_id.object_id.desc or '')
                            ws.write(row, 6, part.space_id and part.space_id.name or '')
                            ws.write(row, 7, part.partner_id and part.partner_id.name or line.partner_id.name)
                            ws.write(row, 8, line.description and line.description or '')
                            ws.write(row, 9, datetime.strftime(part.date,'%Y-%m-%d'))
                            ws.write(row, 10, product.qty_available or 0)
                            ws.write(row, 11, qty_location or 0)
                            ws.write(row, 12, line.product_uom.name)
                            ws.write(row, 13, qty_budget)                        #Presupuesto
                            ws.write(row, 14, product.standard_price)            #Presupuesto
                            ws.write(row, 15, qty_budget*product.standard_price) #Presupuesto
                            ws.write(row, 16, line.product_uom_qty)    #Ejecutado
                            ws.write(row, 17, line.price_unit)         #Ejecutado
                            ws.write(row, 18, line.price_subtotal)     #Ejecutado
                            if quantity_dif < 0:
                                ws.write(row, 19, quantity_dif,style_negative)
                            else:
                                ws.write(row, 19, quantity_dif)
                            if amount_dif < 0:
                                ws.write(row, 20, amount_dif,style_negative)
                            else:
                                ws.write(row, 20, amount_dif)
                            row += 1

                # Mano de Obra desde Orden de TRabajo (Si esta instalado bim_workorder)
                if workorder_active and workorders:
                    bwor_obj = self.env['bim.workorder.resources']
                    for word in workorders:
                        for bwoc in word.concept_ids:
                            lines_with = bwor_obj.search([('workorder_concept_id','=',bwoc.id),('workorder_id','=',bwoc.workorder_id.id)])
                            lines_out = bwor_obj.search([('workorder_id','=',bwoc.workorder_id.id),('departure_id','=',bwoc.concept_id.id)])
                            lines = lines_with + lines_out
                            lines_mo = lines.filtered(lambda x:x.qty_execute > 0)

                            for line in lines_mo:
                                product = line.resource_id.product_id if line.type == 'budget_in' else line.product_id
                                concept = line.concept_id if line.type == 'budget_in' else line.departure_id
                                qty_location = Quants._get_available_quantity(product,location)
                                qty_budget = self.get_quantity(product,concept,word.space_id)
                                quantity_dif = qty_budget-line.qty_execute
                                amount_dif = (qty_budget*product.standard_price)-line.duration_real*product.standard_price
                                ws.write(row, 0, product.default_code or '')
                                ws.write(row, 1, product.display_name)
                                ws.write(row, 2, word.name)
                                ws.write(row, 3, concept and concept.budget_id.display_name or '')
                                ws.write(row, 4, concept and concept.name or '')
                                ws.write(row, 5, word.object_id and word.object_id.desc or '')
                                ws.write(row, 6, word.space_id and word.space_id.name or '')
                                ws.write(row, 7, '')
                                ws.write(row, 8, line.reason or '')
                                ws.write(row, 9, datetime.strftime(line.date_start,'%Y-%m-%d'))
                                ws.write(row, 10, product.qty_available or 0)
                                ws.write(row, 11, qty_location or 0)
                                ws.write(row, 12, product.uom_id.name)
                                ws.write(row, 13, qty_budget)                        #Presupuesto
                                ws.write(row, 14, product.standard_price)            #Presupuesto
                                ws.write(row, 15, qty_budget*product.standard_price) #Presupuesto
                                ws.write(row, 16, line.duration_real)                            #Ejecutado
                                ws.write(row, 17, product.standard_price)                      #Ejecutado
                                ws.write(row, 18, line.duration_real*product.standard_price)     #Ejecutado
                                if quantity_dif < 0:
                                    ws.write(row, 19, quantity_dif,style_negative)
                                else:
                                    ws.write(row, 19, quantity_dif)
                                if amount_dif < 0:
                                    ws.write(row, 20, amount_dif,style_negative)
                                else:
                                    ws.write(row, 20, amount_dif)
                                row += 1

            # Equipos (Partes)
            if self.equipment:
                for part in parts:
                    for line in part.lines_ids:
                        if line.resource_type == 'Q':
                            product = line.name
                            qty_location = Quants._get_available_quantity(product,location)
                            qty_budget = self.get_quantity(product,part.concept_id,part.space_id)
                            quantity_dif = qty_budget-line.product_uom_qty
                            amount_dif = (qty_budget*product.standard_price)-line.price_subtotal
                            ws.write(row, 0, product.default_code or '')
                            ws.write(row, 1, product.display_name)
                            ws.write(row, 2, line.part_id.name)
                            ws.write(row, 3, part.concept_id and part.concept_id.budget_id.display_name or '')
                            ws.write(row, 4, part.concept_id and part.concept_id.name or '')
                            ws.write(row, 5, part.space_id.object_id and part.space_id.object_id.desc or '')
                            ws.write(row, 6, part.space_id and part.space_id.name or '')
                            ws.write(row, 7, part.partner_id and part.partner_id.name or line.partner_id.name)
                            ws.write(row, 8, line.description and line.description or '')
                            ws.write(row, 9, datetime.strftime(part.date,'%Y-%m-%d'))
                            ws.write(row, 10, product.qty_available or 0)
                            ws.write(row, 11, qty_location or 0)
                            ws.write(row, 12, line.product_uom.name)
                            ws.write(row, 13, qty_budget)                         #Presupuesto
                            ws.write(row, 14, product.standard_price)             #Presupuesto
                            ws.write(row, 15, qty_budget*product.standard_price)  #Presupuesto
                            ws.write(row, 16, line.product_uom_qty)    #Ejecutado
                            ws.write(row, 17, line.price_unit)         #Ejecutado
                            ws.write(row, 18, line.price_subtotal)     #Ejecutado
                            if quantity_dif < 0:
                                ws.write(row, 19, quantity_dif,style_negative)
                            else:
                                ws.write(row, 19, quantity_dif)
                            if amount_dif < 0:
                                ws.write(row, 20, amount_dif,style_negative)
                            else:
                                ws.write(row, 20, amount_dif)
                            row += 1


            # aqui va asistencia detallada
            if self.attendance:
                for attendance in attendances:
                    att_qty_budget = 0
                    hour_price = 0
                    if attendance.sudo().concept_id and attendance.sudo().employee_id.bim_resource_id:
                        att_qty_budget = self.get_budget_quantity_hours(attendance.concept_id, attendance.sudo().employee_id.bim_resource_id)
                        hour_price = attendance.sudo().employee_id.bim_resource_id.standard_price
                    quantity_dif = round(att_qty_budget - attendance.worked_hours,2)
                    amount_dif = (att_qty_budget * hour_price) - attendance.attendance_cost
                    dates = str(datetime.strftime(attendance.check_in, '%Y-%m-%d'))
                    if attendance.check_out:
                        dates += ' - ' + str(datetime.strftime(attendance.check_out, '%Y-%m-%d'))
                    ws.write(row, 0, str(attendance.id))
                    ws.write(row, 1, attendance.sudo().employee_id.bim_resource_id.display_name if attendance.sudo().employee_id.bim_resource_id else attendance.sudo().employee_id.name)
                    ws.write(row, 2, _("Attendance"))
                    ws.write(row, 3, attendance.budget_id.display_name if attendance.budget_id else '')
                    ws.write(row, 4, attendance.concept_id.name if attendance.concept_id else '')
                    ws.write(row, 5, '')
                    ws.write(row, 6, '')
                    ws.write(row, 7, attendance.employee_id.name)
                    ws.write(row, 8, attendance.description or '')
                    ws.write(row, 9, dates)
                    ws.write(row, 10, '')
                    ws.write(row, 11, '')
                    ws.write(row, 12, attendance.sudo().employee_id.bim_resource_id.uom_id.name if attendance.sudo().employee_id.bim_resource_id else '')
                    ws.write(row, 13, att_qty_budget)  # Presupuesto
                    ws.write(row, 14, round(hour_price,2))  # Presupuesto
                    ws.write(row, 15, round(att_qty_budget * hour_price,2))  # Presupuesto ver esto
                    ws.write(row, 16, round(attendance.worked_hours,2))  # Ejecutado
                    ws.write(row, 17, round(attendance.hour_cost,2))  # Ejecutado
                    ws.write(row, 18, round(attendance.attendance_cost,2))  # Ejecutado
                    if quantity_dif < 0:
                        ws.write(row, 19, quantity_dif, style_negative)
                    else:
                        ws.write(row, 19, quantity_dif)
                    if amount_dif < 0:
                        ws.write(row, 20, amount_dif, style_negative)
                    else:
                        ws.write(row, 20, amount_dif)
                    row += 1

            #aqui van facturas de compras y rectificativas
            if self.invoice:
                for product in invoice_products:
                    qty_location = Quants._get_available_quantity(product, location)
                    for invoice in invoice_records:
                        for concept in invoice_concepts:
                            budget = concept.budget_id if concept.budget_id else False
                            product_invoiced_price = 0
                            product_invoiced_qty = 0
                            product_invoiced_price_total = 0
                            any_product = False
                            for line in invoice_lines.filtered_domain([('product_id','=',product.id),('concept_id','=',concept.id),('move_id','=',invoice.id)]):
                                factor = 1
                                any_product = True
                                if line.move_id.move_type == 'in_refund':
                                    factor = -1
                                if self.env.company.include_vat_in_indicators:
                                    product_invoiced_price_total += line.price_total * factor
                                else:
                                    product_invoiced_price_total += line.price_subtotal * factor
                                product_invoiced_price += line.price_unit * factor
                                product_invoiced_qty += line.quantity * factor
                            if any_product:
                                qty_budget = self.get_quantity(product, concept, False)
                                quantity_dif = qty_budget - product_invoiced_qty
                                amount_dif = (qty_budget * product.standard_price) - (product_invoiced_qty * product.standard_price)

                                ws.write(row, 0, product.default_code or '')
                                ws.write(row, 1, product.display_name)
                                ws.write(row, 2, invoice.name)
                                ws.write(row, 3, budget and budget.display_name or '')
                                ws.write(row, 4, concept and concept.name or '')
                                ws.write(row, 5, '')
                                ws.write(row, 6, '')
                                ws.write(row, 7, invoice.partner_id.display_name)
                                ws.write(row, 8, invoice.narration or '')
                                ws.write(row, 9, str(invoice.invoice_date))
                                ws.write(row, 10, '')
                                ws.write(row, 11, qty_location or 0)
                                ws.write(row, 12, product.uom_id.name)
                                ws.write(row, 13, qty_budget)  # Presupuesto
                                ws.write(row, 14, product.standard_price)  # Presupuesto
                                ws.write(row, 15, qty_budget * product.standard_price)  # Presupuesto
                                ws.write(row, 16, product_invoiced_qty)  # Ejecutado
                                ws.write(row, 17, round(product_invoiced_price_total/product_invoiced_qty,2) if product_invoiced_qty > 0 else 0 )  # Ejecutado
                                ws.write(row, 18, product_invoiced_price_total)  # Ejecutado
                                if quantity_dif < 0:
                                    ws.write(row, 19, quantity_dif, style_negative)
                                else:
                                    ws.write(row, 19, quantity_dif)

                                if amount_dif < 0:
                                    ws.write(row, 20, amount_dif, style_negative)
                                else:
                                    ws.write(row, 20, amount_dif)
                                row += 1

                        product_invoiced_price = 0
                        product_invoiced_qty = 0
                        product_invoiced_price_total = 0
                        without_concept = False
                        for line in invoice_lines.filtered_domain(
                                [('product_id', '=', product.id), ('concept_id', '=', False),('move_id','=',invoice.id)]):
                            factor = 1
                            without_concept = True
                            if line.move_id.move_type == 'in_refund':
                                factor = -1
                            if self.env.company.include_vat_in_indicators:
                                product_invoiced_price_total += line.price_total * factor
                            else:
                                product_invoiced_price_total += line.price_subtotal * factor
                            product_invoiced_price += line.price_unit * factor
                            product_invoiced_qty += line.quantity * factor
                        if without_concept:
                            qty_budget = 0#self.get_quantity(product, concept, False)
                            quantity_dif = qty_budget - product_invoiced_qty
                            amount_dif = (qty_budget * product.standard_price) - (product_invoiced_qty * product.standard_price)

                            ws.write(row, 0, product.default_code or '')
                            ws.write(row, 1, product.display_name)
                            ws.write(row, 2, invoice.name)
                            ws.write(row, 3, line.budget_id.display_name if line.budget_id else '')
                            ws.write(row, 4, '')
                            ws.write(row, 5, '')
                            ws.write(row, 6, '')
                            ws.write(row, 7, invoice.partner_id.display_name)
                            ws.write(row, 8, '')
                            ws.write(row, 9, str(invoice.invoice_date))
                            ws.write(row, 10, '')
                            ws.write(row, 11, qty_location or 0)
                            ws.write(row, 12, product.uom_id.name)
                            ws.write(row, 13, qty_budget)  # Presupuesto
                            ws.write(row, 14, product.standard_price)  # Presupuesto
                            ws.write(row, 15, qty_budget * product.standard_price)  # Presupuesto
                            ws.write(row, 16, product_invoiced_qty)  # Ejecutado
                            ws.write(row, 17, round(product_invoiced_price_total / product_invoiced_qty,
                                                    2) if product_invoiced_qty > 0 else 0)  # Ejecutado
                            ws.write(row, 18, product_invoiced_price_total)  # Ejecutado
                            if quantity_dif < 0:
                                ws.write(row, 19, quantity_dif, style_negative)
                            else:
                                ws.write(row, 19, quantity_dif)

                            if amount_dif < 0:
                                ws.write(row, 20, amount_dif, style_negative)
                            else:
                                ws.write(row, 20, amount_dif)
                            row += 1

            if self.resource_all:
                for balance in self.project_id.opening_balance_ids:
                    ws.write(row, 0, balance.name)
                    ws.write(row, 1, _("Opening Balance"))
                    ws.write(row, 2, '')
                    ws.write(row, 3, balance.budget_id.display_name if balance.budget_id else '')
                    ws.write(row, 4, balance.concept_id.name if balance.concept_id else '')
                    ws.write(row, 5, '')
                    ws.write(row, 6, '')
                    ws.write(row, 7, '')
                    ws.write(row, 8, '')
                    ws.write(row, 9, '')
                    ws.write(row, 10, '')
                    ws.write(row, 11, '')
                    ws.write(row, 12, '')
                    ws.write(row, 13, '')  # Presupuesto
                    ws.write(row, 14, '')  # Presupuesto
                    ws.write(row, 15, '')  # Presupuesto
                    ws.write(row, 16, '')  # Ejecutado
                    ws.write(row, 17, '')
                    ws.write(row, 18, balance.amount)
                    ws.write(row, 19, '')
                    ws.write(row, 20, '')
                    row += 1
                    #.Exportacion
        fp = io.BytesIO()
        wb.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        data_b64 = base64.encodebytes(data)
        attach = self.env['ir.attachment'].create({
            'name': '%s.%s'%(project.name,self.doc_type),
            'type': 'binary',
            'datas': data_b64  })
        url = '/web/content/?model=ir.attachment'
        url += '&id={}&field=datas&download=true&filename={}'.format(attach.id,attach.name)
        return {'type': 'ir.actions.act_url', 'url': url, 'target': 'self'}
