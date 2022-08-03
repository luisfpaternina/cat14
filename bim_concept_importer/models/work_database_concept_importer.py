# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
import base64
from odoo.exceptions import UserError
import xlrd
import os
RESOURSES = ['MO','MAT','EQUIPO','OTROS','%']

class WorkDatabaseConceptImporter(models.Model):
    _description = "Work Database Concept Importer"
    _name = 'work.database.concept.importer'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    name = fields.Char('Code', default="New", tracking=True)
    project_id = fields.Many2one('bim.project', 'Project', required=True, tracking=True, ondelete='cascade')
    excel_file = fields.Binary('Excel File', required=True, tracking=True)
    filename = fields.Char('File name')
    state = fields.Selection(
        [('to_execute', 'To execute'), ('ongoing', 'In process'), ('done', 'Done'), ('error', 'Error')], 'Status',
        default='to_execute', tracking=True)
    error = fields.Text(readonly=True)
    budget_id = fields.Many2one('bim.budget', 'Created budget', readonly=True, ondelete='cascade')

    budget_name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', 'Responsable', readonly=True, required=True,
                              default=lambda self: self.env.user)
    version = fields.Selection([('1000', 'Mode 1000'),('2000', 'Mode 2000')], 'Version', default='1000', required=True,
                               tracking=True)
    product_id = fields.Many2one('product.product', 'Default product',
                                 default=lambda self: self.env.ref('base_bim_2.default_product',
                                                                   raise_if_not_found=False))
    create_all_products = fields.Boolean('Create non-existent products')
    product_cost_or_price = fields.Selection([('price', 'Sale Price'), ('cost', 'Product Cost')],
                                             string='Assign to', default='cost')

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('work.database.concept.importer') or "New"
        return super().create(vals)

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            budget_count = self.project_id.budget_count + 1
            self.budget_name = _("Budget: {} {}").format(budget_count, self.project_id.name)
        else:
            self.budget_name = _("Budget")


    @api.model
    def excel_validator(self, xml_name):
        name, extension = os.path.splitext(xml_name)
        return True if extension in ['.xlsx','.xls'] else False

    def action_import_concepts(self):
        if not self.excel_validator(self.filename):
            raise UserError(_("File must contain excel extension"))
        if self.version == '2000':
            return self.import_2000_template()
        elif self.version == '1000':
            return self.import_1000_template()

    def import_2000_template(self):
        data = base64.b64decode(self.excel_file)
        work_book = xlrd.open_workbook(file_contents=data)
        sheet = work_book.sheet_by_index(0)
        first_row = []
        for col in range(sheet.ncols):
            first_row.append(sheet.cell_value(0, col))
        # validando al cabecera
        if first_row[0] != "PARTIDA":
            raise UserError(_("Please check template header in position: {}").format(0))
        if first_row[1] != "NAT":
            raise UserError(_("Please check template header in position: {}").format(1))
        if first_row[2] != "UNIDAD":
            raise UserError(_("Please check template header in position: {}").format(2))
        if first_row[3] != "DESCRIPCION DE PARTIDA":
            raise UserError(_("Please check template header in position: {}").format(3))
        if first_row[4] != "MEDICION":
            raise UserError(_("Please check template header in position: {}").format(4))
        if first_row[5] != "PRECIO":
            raise UserError(_("Please check template header in position: {}").format(5))
        if first_row[6] != "IMPORTE":
            raise UserError(_("Please check template header in position: {}").format(6))
        new_budget = self.env['bim.budget'].create({'name': self.budget_name,
                                                    'project_id': self.project_id.id,
                                                    'currency_id': self.project_id.currency_id.id
                                                    })
        self.budget_id = new_budget.id

        concept_obj = self.env['bim.concepts']
        product_obj = self.env['product.product']
        uom_obj = self.env['uom.uom']
        line_count = 1
        last_departure = False
        for count, row in enumerate(range(1, sheet.nrows), 2):
            line_count +=1
            val = {}
            for col in range(sheet.ncols):
                if sheet.cell_value(row, 0) == "":
                    break
                else:
                    val[first_row[col]] = sheet.cell_value(row, col)
            try:
                if len(val) > 0:
                    if not '.' in str(val['PARTIDA']) and str(val['NAT']) =="" and str(val['UNIDAD']) =="":
                        self.create_chapter(val, new_budget, concept_obj, uom_obj)
                    elif '.' in str(val['PARTIDA']) and '#' in str(val['PARTIDA']) and str(val['NAT']) =="":
                        self.create_sub_chapter(val, new_budget, concept_obj, uom_obj)
                    elif not '#' in str(val['PARTIDA']) and '.' in str(val['PARTIDA']) and str(val['NAT']) =="":
                        last_departure = self.create_departure(val, new_budget, concept_obj, uom_obj)
                    elif '#' in str(val['PARTIDA']) or '.' in str(val['PARTIDA']) and (str(val['NAT']) in RESOURSES and self.version == '2000'):
                        if last_departure:
                            self.create_resource(val, new_budget, concept_obj, uom_obj, last_departure, product_obj)
                    elif not '#' in str(val['PARTIDA']) and not '.' in str(val['PARTIDA']) and (str(val['NAT']) in RESOURSES and self.version == '2000'):
                        if last_departure:
                            self.create_resource(val, new_budget, concept_obj, uom_obj, last_departure, product_obj)
            except Exception as exp:
                print(exp)
                raise UserError(_("There is a wrong character in line: {}. Please check it!").format(line_count))
        self.state = 'done'
        for concept in new_budget.concept_ids.filtered_domain([('type','=','departure')]):
            if concept.child_ids:
                concept.amount_type = 'compute'

    def import_1000_template(self):
        data = base64.b64decode(self.excel_file)
        work_book = xlrd.open_workbook(file_contents=data)
        sheet = work_book.sheet_by_index(0)
        first_row = []
        for col in range(sheet.ncols):
            first_row.append(sheet.cell_value(0, col))
        # validando al cabecera
        if first_row[0] != "PARTIDA":
            raise UserError(_("Please check template header in position: {}").format(0))
        if first_row[1] != "NAT":
            raise UserError(_("Please check template header in position: {}").format(1))
        if first_row[2] != "UNIDAD":
            raise UserError(_("Please check template header in position: {}").format(2))
        if first_row[3] != "DESCRIPCION DE PARTIDA":
            raise UserError(_("Please check template header in position: {}").format(3))
        if first_row[4] != "MEDICION":
            raise UserError(_("Please check template header in position: {}").format(4))
        if first_row[5] != "PRECIO":
            raise UserError(_("Please check template header in position: {}").format(5))
        if first_row[6] != "IMPORTE":
            raise UserError(_("Please check template header in position: {}").format(6))
        new_budget = self.env['bim.budget'].create({'name': self.budget_name,
                                                    'project_id': self.project_id.id,
                                                    'currency_id': self.project_id.currency_id.id
                                                    })
        self.budget_id = new_budget.id

        concept_obj = self.env['bim.concepts']
        uom_obj = self.env['uom.uom']
        line_count = 1
        for count, row in enumerate(range(1, sheet.nrows), 2):
            line_count +=1
            val = {}
            for col in range(sheet.ncols):
                if sheet.cell_value(row, 0) == "":
                    break
                else:
                    val[first_row[col]] = sheet.cell_value(row, col)
            try:
                if len(val) > 0:
                    if not '.' in str(val['PARTIDA']) and str(val['UNIDAD']) =="":
                        self.create_chapter(val, new_budget, concept_obj, uom_obj)
                    elif '.' in str(val['PARTIDA']) and '#' in str(val['PARTIDA']):
                        self.create_sub_chapter(val, new_budget, concept_obj, uom_obj)
                    elif not '#' in str(val['PARTIDA']) and '.' in str(val['PARTIDA']):
                        self.create_departure(val, new_budget, concept_obj, uom_obj)

            except Exception as exp:
                raise UserError(_("There is a wrong character in line: {}. Please check it!").format(line_count))
        self.state = 'done'
        for concept in new_budget.concept_ids.filtered_domain([('type','=','departure')]):
            if concept.child_ids:
                concept.amount_type = 'compute'

    def create_chapter(self, val, budget, concept_obj, uom_obj):
        code = str(val['PARTIDA']).replace('#','')
        name = val['DESCRIPCION DE PARTIDA']
        uom_id = False
        if val['UNIDAD'] != "":
            uom_id = uom_obj.search(['|',('name','=',val['UNIDAD']),('alt_names','ilike',val['UNIDAD'])], limit=1)
        if name == "":
            name = _("Empty")
        concept_obj.create({
            'code': code,
            'name': name,
            'uom_id': uom_id.id if uom_id else False,
            'budget_id': budget.id,
            'type': 'chapter'
        })

    def create_sub_chapter(self, val, budget, concept_obj, uom_obj):
        code = str(val['PARTIDA']).replace('#','')
        name = val['DESCRIPCION DE PARTIDA']
        uom_id = False
        level = code.count('.')
        code_splitted = code.split('.')
        departure_code_len = len(code_splitted[level])
        parent_code = code[:-departure_code_len - 1]
        parent_id = concept_obj.search([('code', '=', parent_code), ('budget_id', '=', budget.id)])
        if val['UNIDAD'] != "":
            uom_id = uom_obj.search(['|',('name','=',val['UNIDAD']),('alt_names','ilike',val['UNIDAD'])], limit=1)
        if name == "":
            name = _("Empty")
        concept_obj.create({
            'code': code,
            'parent_id': parent_id.id if parent_id else False,
            'name': name,
            'uom_id': uom_id.id if uom_id else False,
            'budget_id': budget.id,
            'type': 'chapter'
        })

    def create_departure(self, val, budget, concept_obj, uom_obj):
        code = str(val['PARTIDA']).replace('#','')
        level = code.count('.')
        code_splitted = code.split('.')
        departure_code_len = len(code_splitted[level])
        parent_code = code[:-departure_code_len-1]
        parent_id = concept_obj.search([('code','=',parent_code),('budget_id','=',budget.id)])
        quantity = 1
        price = 0
        if not '#' in str(val['PARTIDA']):
            quantity = 0
            if (not '-' in str(val['MEDICION']) and val['MEDICION'] != '') or (len(str(val['MEDICION']))>1 and val['MEDICION'] != '' and float(val['MEDICION']) < 0):
                quantity = val['MEDICION']
            if (len(str(val['PRECIO']))>1 and val['PRECIO'] != ''):#(not '-' in str(val['PRECIO']) and val['PRECIO'] != '') or
                price = val['PRECIO']
            if (str(type(val['IMPORTE'])) != "<class 'float'>") or (str(type(val['IMPORTE'])) == "<class 'float'>" and float(val['IMPORTE']) == 0):
                return False
        name = val['DESCRIPCION DE PARTIDA']
        concept_type = 'departure'
        uom_id = False
        if val['UNIDAD'] != "":
            uom_id = uom_obj.search(['|', ('name', '=', val['UNIDAD']), ('alt_names', 'ilike', val['UNIDAD'])], limit=1)
        if not parent_id:
            count = 1
            while count <= level:
                parent_id = concept_obj.search([('code', '=', code_splitted[level-count]), ('budget_id', '=', budget.id)])
                count += 1
                if parent_id:
                    break
        if not parent_id:
            concept_type = 'chapter'

        if name == "":
            name = _("Empty")
        concept = concept_obj.create({
            'code': code,
            'name': name,
            'budget_id': budget.id,
            'uom_id': uom_id.id if uom_id else False,
            'parent_id': parent_id.id if parent_id else False,
            'quantity': float(quantity),
            'amount_fixed': float(price),
            'amount_type': 'fixed',
            'type': concept_type
        })
        return concept

    def create_resource(self, val, budget, concept_obj, uom_obj, last_parent_id, product_obj):
        category = self.env.company.bim_product_category_id
        code = str(val['PARTIDA'])
        quantity = 1
        price = 0
        if not '#' in str(val['PARTIDA']):
            quantity = 0
            if (not '-' in str(val['MEDICION']) and val['MEDICION'] != '') or (len(str(val['MEDICION']))>1 and val['MEDICION'] != '' and float(val['MEDICION']) < 0):
                quantity = val['MEDICION']
            if (len(str(val['PRECIO']))>1 and val['PRECIO'] != ''):#(not '-' in str(val['PRECIO']) and val['PRECIO'] != '') or
                price = val['PRECIO']
            if (str(type(val['IMPORTE'])) != "<class 'float'>") or (str(type(val['IMPORTE'])) == "<class 'float'>" and float(val['IMPORTE']) == 0) and str(val['NAT']) != "%":
                return False
        name = val['DESCRIPCION DE PARTIDA']
        concept_type = 'material'
        res_type = 'M'
        if str(val['NAT']) == "MO":
            concept_type = 'labor'
            res_type = 'H'
        elif str(val['NAT']) == "EQUIPO":
            concept_type = 'equip'
            res_type = 'Q'
        elif str(val['NAT']) == "%":
            concept_type = 'aux'

        uom_id = False
        if val['UNIDAD'] != "":
            uom_id = uom_obj.search(['|', ('name', '=', val['UNIDAD']), ('alt_names', 'ilike', val['UNIDAD'])], limit=1)
            if not uom_id:
                uom_id = uom_obj.search(['|', ('name', '=', 'Unidades'), ('alt_names', 'ilike', 'ud')], limit=1)
        if name == "":
            name = _("Empty")
        product = product_obj.search(['|', ('default_code', '=', code), ('barcode', '=', code)],
                                     limit=1) if self.create_all_products else self.product_id

        concept = concept_obj.create({
            'code': code,
            'name': name,
            'budget_id': budget.id,
            'uom_id': uom_id.id if uom_id else False,
            'parent_id': last_parent_id.id if last_parent_id else False,
            'quantity': float(quantity),
            'amount_fixed': float(price),
            'amount_type': 'fixed',
            'type': concept_type
        })
        if not product and concept_type != 'aux':
            product = product_obj.create({
                'name': name,
                'resource_type': res_type,
                'type': 'product' if concept_type == 'material' else 'service',
                'list_price': float(price) if self.product_cost_or_price == 'price' else 0,
                'standard_price': float(price) if self.product_cost_or_price == 'cost' else 0,
                'default_code': code,
                'categ_id': category.id,
                'uom_id': uom_id.id if uom_id else False,
                'uom_po_id': uom_id.id if uom_id else False,
            })
        if concept_type != 'aux':
            concept.product_id = product

    def unlink(self):
        for record in self:
            if record.state != "to_execute":
                raise UserError(_("Importer Records can be only deleted in 'To Execute' state!"))
        return super().unlink()

