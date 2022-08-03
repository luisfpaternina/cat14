# coding: utf-8
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import xlwt
from io import BytesIO
import base64
from datetime import datetime

class BimResourceReportWizard(models.TransientModel):
    _name = 'bim.resource.report.wizard'
    _description = 'Buget Resource Report'

    def _default_budget(self):
        return self.env['bim.budget'].browse(self._context.get('active_id'))


    material = fields.Boolean(string="Materials",default=True)
    equipment = fields.Boolean(string="Equipment",default=True)
    labor = fields.Boolean(string="Labor",default=True)
    aux = fields.Boolean(string="Other",default=True)
    budget_id = fields.Many2one('bim.budget', "Budget", required=True, default=_default_budget)
    resource_all = fields.Boolean(default=True,string="All")
    filter_categ = fields.Boolean(string="Category Filter")
    category_id = fields.Many2one('product.category', "Category")

    def recursive_amount(self, resource, parent, amount=None):
        amount = amount is None and resource.balance or amount
        if parent.type == 'departure':
            amount_partial = amount * parent.quantity
            return self.recursive_amount(resource,parent.parent_id,amount_partial)
        else:
            return amount * parent.quantity

    def recursive_quantity(self, resource, parent, qty=None):
        qty = qty is None and resource.quantity or qty
        if parent.type == 'departure':
            qty_partial = qty * parent.quantity
            return self.recursive_quantity(resource,parent.parent_id,qty_partial)
        else:
            return qty * parent.quantity

    @api.model
    def get_total_aux(self,resource):
        total = 0
        if resource.balance > 0:
            total += self.recursive_amount(resource,resource.parent_id,None)
        return total

    @api.model
    def get_total(self,resource_id):
        budget = self.budget_id
        records = budget.concept_ids.filtered(lambda c: c.product_id.id == resource_id)
        total = 0

        for rec in records:
            if rec.balance > 0:
                total += self.recursive_amount(rec,rec.parent_id,None)
        return total

    @api.model
    def get_quantity_aux(self,resource):
        total_qty = 0
        if resource.quantity > 0:
            total_qty += self.recursive_quantity(resource,resource.parent_id,None)
        return total_qty

    @api.model
    def get_quantity(self,resource_id):
        budget = self.budget_id
        records = budget.concept_ids.filtered(lambda c: c.product_id.id == resource_id)
        total_qty = 0
        for rec in records:
            if rec.quantity > 0:
                total_qty += self.recursive_quantity(rec,rec.parent_id,None)
        return total_qty

    @api.model
    def get_weight(self,resource_id):
        budget = self.budget_id
        records = budget.concept_ids.filtered(lambda c: c.product_id.id == resource_id)
        total_weight = 0
        for rec in records:
            total_weight += rec.weight
        return total_weight

    @api.model
    def get_function(self,aux):
        values = self.budget_id.concept_ids
        resources = False
        if aux:
            resources = values.filtered(lambda c: c.type == 'aux')
        return resources

    @api.model
    def get_resources(self,material,labor,equipment):
        values = self.budget_id.concept_ids
        domain = []
        if material:
            domain.append('material')
        if equipment:
            domain.append('equip')
        if labor:
            domain.append('labor')
        resources = values.filtered(lambda c: c.type in domain).mapped('product_id')
        if self.filter_categ:
            resources = resources.filtered(lambda p: p.categ_id.id == self.category_id.id)
        return resources

    @api.model
    def get_resources_total(self,material,labor,equipment,aux):
        values = self.budget_id.concept_ids
        result = []
        if material:
            total_material = 0
            resources = values.filtered(lambda c: c.type in 'material').mapped('product_id')
            if self.filter_categ:
                resources = resources.filtered(lambda p: p.categ_id.id == self.category_id.id)
            for mat in resources:
                total_material += self.get_total(mat.id)
            result.append({'name':_('Total Materials'),'amount': total_material})

        if equipment:
            total_equip = 0
            resources = values.filtered(lambda c: c.type in 'equip').mapped('product_id')
            if self.filter_categ:
                resources = resources.filtered(lambda p: p.categ_id.id == self.category_id.id)
            for eqp in resources:
                total_equip += self.get_total(eqp.id)
            result.append({'name':_('Total Equipment'),'amount': total_equip})

        if labor:
            total_labor = 0
            resources = values.filtered(lambda c: c.type in 'labor').mapped('product_id')
            if self.filter_categ:
                resources = resources.filtered(lambda p: p.categ_id.id == self.category_id.id)
            for lab in resources:
                total_labor += self.get_total(lab.id)
            result.append({'name':_('Total Labor'),'amount': total_labor})

        if aux:
            total_aux = self.budget_id.amount_total_other
            result.append({'name':_('Total Other'),'amount': total_aux})

        return result


    @api.onchange('equipment', 'material', 'labor','aux')
    def onchange_resource(self):
        self.resource_all = True if (self.equipment and self.material and self.labor and self.aux) else False

    @api.onchange('resource_all')
    def onchange_resource_all(self):
        if not self.resource_all and (self.equipment and self.material and self.labor and self.aux):
            self.equipment = self.material = self.labor = self.aux = False
        elif self.resource_all:
            self.equipment = self.material = self.labor = self.aux = True

    def print_report(self):
        return self.env.ref('base_bim_2.bim_budget_resource').report_action(self)

    def get_resource_type(self,res_type):
        result = ''
        if res_type == 'aux':
            result = _('FUNCTION / ADMINISTRATIVE')
        elif res_type == 'H':
            result = _('LABOR')
        elif res_type == 'M':
            result = _('MATERIAL')
        elif res_type == 'Q':
            result = _('EQUIPMENT')
        return result


    def check_report_xls(self):
        budget = self.budget_id
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet('Resources')
        file_name = 'Resources'
        style_title = xlwt.easyxf('font: name Times New Roman 180, color-index black, bold on; align: wrap yes, horiz center')
        style_border_table_top = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin; font: bold on;')
        style_border_table_details = xlwt.easyxf('borders: bottom thin;')
        worksheet.write_merge(0, 0, 0, 10, _("RESOURCE LIST"), style_title)
        worksheet.write_merge(1,1,0,2, _("Project"))
        worksheet.write_merge(1,1,3,5, budget.name)
        worksheet.write_merge(1,1,6,8, _("Printing Date"))
        if self.filter_categ:
            worksheet.write_merge(1,1,9,11, _("Filter Category"))
        worksheet.write_merge(2,2,0,2, budget.project_id.nombre)
        worksheet.write_merge(2,2,3,5, budget.code)
        worksheet.write_merge(2,2,6,8, datetime.now().strftime('%d-%m-%Y'))
        if self.filter_categ:
            worksheet.write_merge(2,2,9,11, self.category_id.name)

        # Header table
        worksheet.write_merge(4,4,0,0, _("Code"), style_border_table_top)
        worksheet.write_merge(4,4,1,5, _("Resource"), style_border_table_top)
        worksheet.write_merge(4,4,6,6, _("Type"), style_border_table_top)
        worksheet.write_merge(4,4,7,7, _("Unit"), style_border_table_top)
        worksheet.write_merge(4,4,8,8, _("Quantity"), style_border_table_top)
        worksheet.write_merge(4,4,9,9, _("Weight"), style_border_table_top)
        worksheet.write_merge(4,4,10,10, _("Cost"), style_border_table_top)
        resources = self.get_resources(self.material,self.labor,self.equipment)
        functions = self.get_function(self.aux)
        row = 5
        for res in resources:
            weight = round(self.get_weight(res.id),2)
            worksheet.write_merge(row,row,0,0, res.code, style_border_table_details)
            worksheet.write_merge(row,row,1,5, res.name, style_border_table_details)
            worksheet.write_merge(row,row,6,6, self.get_resource_type(res.resource_type), style_border_table_details)
            worksheet.write_merge(row,row,7,7, res.uom_id.name, style_border_table_details)
            worksheet.write_merge(row,row,8,8, round(self.get_quantity(res.id),3), style_border_table_details)
            if weight <= 0:
                worksheet.write_merge(row,row,9,9, "-", style_border_table_details)
            else:
                worksheet.write_merge(row,row,9,9, weight, style_border_table_details)
            worksheet.write_merge(row,row,10,10, round(self.get_total(res.id),2), style_border_table_details)
            row += 1
        if functions:
            for res in functions:
                worksheet.write_merge(row,row,0,0, res.code, style_border_table_details)
                worksheet.write_merge(row,row,1,5, res.name, style_border_table_details)
                worksheet.write_merge(row,row,6,6, self.get_resource_type(res.type), style_border_table_details)
                worksheet.write_merge(row,row,7,7, res.uom_id.name, style_border_table_details)
                worksheet.write_merge(row,row,8,8, res.amount_compute, style_border_table_details)#round(self.get_quantity_aux(res),3)
                worksheet.write_merge(row,row,9,9, "-", style_border_table_details)
                worksheet.write_merge(row,row,10,10, round(self.get_total_aux(res),2), style_border_table_details)
                row += 1

        totals = self.get_resources_total(self.material,self.labor,self.equipment,self.aux)
        for tot in totals:
            worksheet.write_merge(row,row,7,8, tot['name'], style_border_table_details)
            worksheet.write_merge(row,row,9,10, tot['amount'], style_border_table_details)
            row += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        data_b64 = base64.encodebytes(data)
        doc = self.env['ir.attachment'].create({
            'name': '%s.xls' % (file_name),
            'datas': data_b64,
        })

        return {
            'type': "ir.actions.act_url",
            'url': "web/content/?model=ir.attachment&id=" + str(
                doc.id) + "&filename_field=name&field=datas&download=true&filename=" + str(doc.name),
            'target': "self",
            'no_destroy': False,
        }
