import base64
import datetime
import io
import traceback

import bs4
import xlrd

from odoo import api, fields, models, _


class BimImportTemp(models.Model):
    _name = 'bim.import.temp'
    _description = 'Importation Project'
    _inherit = ['mail.thread']
    _rec_name = 'filename'
    _order = 'id desc'

    name = fields.Char('Code', default=_('New'), tracking=True)
    version = fields.Selection([('8.8', 'Excel Template'), ('bc3', 'BC3'), ('ms_xml', 'Project XML')], 'Version', default='8.8', required=True, tracking=True)
    project_id = fields.Many2one('bim.project', 'Project', required=True, tracking=True, ondelete='cascade')
    create_all_products = fields.Boolean('Create non-existent products', tracking=True)
    product_id = fields.Many2one('product.product', 'Default product', default=lambda self: self.env.ref('base_bim_2.default_product', raise_if_not_found=False), tracking=True)
    excel_file = fields.Binary('Excel File', required=True, tracking=True)
    filename = fields.Char('File name')
    state = fields.Selection([('to_execute', 'To execute'), ('ongoing', 'In process'), ('done', 'Done'), ('error', 'Error')], 'Status', default='to_execute', tracking=True)
    error = fields.Text(readonly=True)
    budget_id = fields.Many2one('bim.budget', 'Created budget', readonly=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', 'Responsable', readonly=True, required=True, default=lambda self: self.env.user)
    last_row = fields.Integer('Last Row', readonly=True, tracking=True)
    product_cost_or_price = fields.Selection([('price', 'Precio Venta'), ('cost', 'Costo Producto')],
                                             string='Asignar a', default='cost')
    import_stages = fields.Boolean()

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.import.temp') or _('New')
        return super(BimImportTemp, self).create(vals)

    def action_import(self):
        self.with_context(import_this=self.id).cron_start_import()

    @api.model
    def cron_start_import(self):
        record = self.browse(self.env.context.get('import_this'))
        if not record or record.state not in ['ongoing', 'to_execute']:
            record = self.search([('state', 'in', ['ongoing', 'to_execute'])], limit=1, order='state')
        if record.version == '8.8':
            with io.StringIO() as error_traceback:
                try:
                    record.import_8_8()
                except:
                    traceback.print_exc(file=error_traceback)
                    error_traceback.seek(0)
                    record.write({'state': 'error', 'error': error_traceback.read()})
        elif record.version == 'bc3':
            with io.StringIO() as error_traceback:
                try:
                    record.import_bc3()
                except:
                    traceback.print_exc(file=error_traceback)
                    error_traceback.seek(0)
                    record.write({'state': 'error', 'error': error_traceback.read()})
        elif record.version == 'ms_xml':
            with io.StringIO() as error_traceback:
                try:
                    record.import_ms_xml()
                except:
                    traceback.print_exc(file=error_traceback)
                    error_traceback.seek(0)
                    record.write({'state': 'error', 'error': error_traceback.read()})
        else:
            record.write({'state': 'error', 'error': 'No implemented'})
        return True

    def back_draft(self):
        self.write({'state': 'to_execute'})

    def import_8_8(self):
        types = {
            'Capítulo': 'chapter',
            'Partida': 'departure',
            'Mano de obra': 'labor',
            'Maquinaria': 'equip',
            'Material': 'material',
            'Otros': 'aux',
        }
        res_types = {
            'Mano de obra': 'H',
            'Maquinaria': 'Q',
            'Material': 'M',
            'Otros': 'A'
        }
        data = base64.b64decode(self.excel_file)
        work_book = xlrd.open_workbook(file_contents=data)
        sheet = work_book.sheet_by_index(0)
        budget = self.env['bim.budget']
        concept_obj = departure = self.env['bim.concepts']
        uom_obj = self.env['uom.uom']
        uoms = {}
        for uom in uom_obj.search([]):
            uoms[uom.name] = uom
            for alt_name in (uom.alt_names or '').split(','):
                if not alt_name.strip():
                    continue
                uoms[alt_name.strip()] = uom
        units_id = self.env.ref('uom.product_uom_unit').id
        next_row_is_departure_note = False
        product_obj = self.env['product.product']
        formula_obj = self.env['bim.formula']
        last_row = self.last_row
        read_rows = 0
        limit = int(self.env['ir.config_parameter'].get_param('bim.import.temp.limit')) or 5000
        budget = self.budget_id
        if budget.space_ids:
            default_space = budget.space_ids[0]
        else:
            default_space = self.env.ref('base_bim_2.default_bim_budget_space')
        category = self.env.company.bim_product_category_id
        # Creamos un set de todos los conceptos "sin hijos", de modo que podamos
        # asignarle padre cuando encontremos la columna "parcial", usando el index
        # de ese concepto para tomar todos los hijos despúes de él y asignarles así un padre,
        # para luego sacarlos de la lista.
        concepts_without_parent = budget.concept_ids.filtered_domain([('parent_id', '=', False)])
        for i, row in enumerate(list(sheet.get_rows())[last_row:], last_row):
            read_rows += 1

            if i == 0:  # Si es la primera línea, solo tomo el nombre para crear el presupuesto.
                budget = budget.create({
                    'name': row[0].value,
                    'project_id': self.project_id.id,
                    'currency_id': self.project_id.currency_id.id,
                })
                continue
            elif i in [1, 2]:  # Las 2 siguientes líneas las puedo ignorar.
                continue
            # Tomamos la naturaleza
            nat = 'aux' if '%' in str(row[0].value).strip() else types.get(row[1].value)
            # Si encontramos un capítulo luego de haber pasado el límite, y no
            # quedan padres en la pila, detenemos el proceso para continuarlo
            # en una siguiente interación.
            if nat == 'chapter' and read_rows >= limit:
                read_rows -= 1
                break
            # Si la fila tiene mas de 7 columnas, es porque el archivo es de mediciones
            has_measures = len(row) > 7
            # Si la siguiente línea viene luego de una partida, y no tiene naturaleza,
            # ni valores en la columna CanPres (E cuando no tiene mediciones, K cuando tiene)
            # es una nota de partida, la tomamos y continuamos.
            if next_row_is_departure_note and not nat and row[3].value and row[10 if has_measures else 4].ctype == 0:
                departure.note = row[3].value
                next_row_is_departure_note = False
                continue

            # Verificamos la columna "parcial" (J si tiene las mediciones, D si no tiene)
            parcial_row = row[9 if has_measures else 3]
            parent_close_code = parcial_row.value.strip() if (parcial_row.ctype == 1 and not row[0].value and not row[1].value and not row[2].value) else False
            # Es posible que en presto 19 la columna "parcial" inicie con la palabra "Total", así que se la quitaremos
            if isinstance(parent_close_code, str):
                parent_close_code = parent_close_code.replace('Total', '').replace('total', '').replace('TOTAL', '').strip()

            # Si tenemos código en la "parcial", buscamos el index en el set de
            # padres, para tomar a todos los conceptos después de este y así
            # asignarles el padre, para luego sacarlos.
            if parent_close_code:
                concetps_without_parent_codes = concepts_without_parent.mapped('code')
                index = rindex(concetps_without_parent_codes, parent_close_code) if parent_close_code in concetps_without_parent_codes else -1
                # Si casualmente no está ese código en el listado de padres... ¿no se?
                if index >= 0:
                    parent = concepts_without_parent[index]
                    children = concepts_without_parent[index + 1:]
                    children.write({'parent_id': parent.id})
                    # Asignamos la secuencia a cada uno de sus hijos
                    for seq, child in enumerate(children, 1):
                        child.sequence = seq
                    concepts_without_parent -= children
                    if parent.child_ids:
                        parent.amount_type = 'compute'  # Si ya es padre, entonces lo hacemos calculado.

            uom_id = uoms.get(row[2].value, uom_obj.browse())
            # Creamos el concepto base, luego nos preocupamos de su naturaleza.
            concept = concept_obj.create({
                'code': str(row[0].value).strip(),
                'type': nat,
                'uom_id': uom_id.id,
                'name': row[3].value,
                'budget_id': budget.id,
                'quantity': float(row[10 if has_measures else 4].value),
                'amount_fixed': float(row[11 if has_measures else 5].value),
                'amount_type': 'fixed'  # Será manual hasta que le encontremos un hijo
            }) if nat else concept_obj.browse()
            # Este concepto recién creado lo añadimos al set de conceptos sin padre
            concepts_without_parent += concept

            # Si es una partida, guardo este concepto como la "última partida"
            # y le indicamos que la siguiente línea es para la nota de la partida.
            if nat == 'departure':
                departure = concept
                next_row_is_departure_note = True
            # Si contiene al menos una naturaleza, y sabemos que no es ni un
            # capítulo ni una partida, entonces es una obra, material o función.
            elif nat and nat != 'chapter':
                # Tratamos de buscar un producto con el mismo nombre
                code = str(row[0].value).strip()
                product = product_obj.search(['|', ('default_code', '=', code), ('barcode', '=', code)], limit=1) if self.create_all_products else self.product_id
                if not product:
                    # Y si no lo encontramos, se crea
                    res_type = res_types.get(row[1].value)
                    product = product_obj.create({
                        'name': row[3].value,
                        'resource_type': res_type,
                        'type': 'product' if res_type == 'M' else 'service',
                        'standard_price': float(row[11 if has_measures else 5].value) if self.product_cost_or_price == 'cost' else 0,
                        'list_price': float(row[11 if has_measures else 5].value) if self.product_cost_or_price == 'price' else 0,
                        'default_code': str(row[0].value).strip(),
                        'categ_id': category.id,
                        'uom_id': uom_id.id or units_id,
                        'uom_po_id': uom_id.id or units_id,
                    })
                concept.product_id = product
            # Si esta línea no tiene naturaleza, y tampoco es la siguiente luego
            # de una partida, pero si tiene un comentario, entonces es una medición,
            # se la asignamos a la partida.
            elif row[4].value and has_measures:
                formula = formula_obj.search(['|', ('formula', 'ilike', row[10].value), ('name', 'ilike', row[10].value)], limit=1) if row[10].value else formula_obj.browse()
                if not formula and row[10].value:
                    # La fórmula podría fallar, así que si da problemas, no la cargamos.
                    try:
                        X = x = b = B = float(row[6].value)
                        Y = y = c = C = float(row[7].value)
                        Z = z = d = D = float(row[8].value)
                        eval(str(row[10].value))
                        valid = True
                    except (SyntaxError, NameError):
                        valid = False
                    formula = formula_obj.create({
                        'name': row[10].value,
                        'formula': row[10].value,
                    }) if valid else formula_obj.browse()
                measuring_vals = {
                    'space_id': default_space.id,
                    'name': row[4].value,
                    'qty': int(row[5].value),
                    'length': float(row[6].value),
                    'width': float(row[7].value),
                    'height': float(row[8].value),
                    'amount_subtotal': float(row[9].value),
                    'formula': formula.id,
                }
                departure.write({
                    'measuring_ids': [(0, 0, measuring_vals)]
                })
        return self.write({
            'state': 'ongoing' if read_rows >= limit else 'done',
            'last_row': last_row + read_rows,
            'budget_id': budget.id,
        })

    def import_bc3(self):
        data = base64.b64decode(self.excel_file).decode('latin-1')
        read_rows = 0
        limit = int(self.env['ir.config_parameter'].get_param('bim.import.temp.limit')) or 5000
        budget = self.budget_id or self.budget_id.create({'name': 'N/A',
                                                          'project_id': self.project_id.id,
                                                          'date_end': fields.Date.today(),
                                                          'currency_id': self.project_id.currency_id.id})
        if budget.space_ids:
            default_space = budget.space_ids[0]
        else:
            default_space = self.env.ref('base_bim_2.default_bim_budget_space')
        last_row = self.last_row
        formula_obj = self.env['bim.formula']
        concept_obj = self.env['bim.concepts']
        uom_obj = self.env['uom.uom']
        uoms = {}
        for uom in uom_obj.search([]):
            uoms[uom.name] = uom
            for alt_name in (uom.alt_names or '').split(','):
                if not alt_name.strip():
                    continue
                uoms[alt_name.strip()] = uom
        units_id = self.env.ref('uom.product_uom_unit').id
        product_obj = self.env['product.product']
        category = self.env.company.bim_product_category_id
        children_codes = {}
        concepts = budget.concept_ids
        nats = ['not_used', 'labor', 'equip', 'material']
        res_types = ['A', 'H', 'Q', 'M']
        pending = ''
        rows = data.split('\n')
        for row in rows[last_row:]:
            row = row.strip()
            read_rows += 1
            if read_rows > limit:
                break
            if row and pending:
                row = pending + row
                pending = ''

            next_row = rows[last_row + read_rows] if len(rows) > last_row + read_rows else False
            if row and next_row and next_row[0] != '~':
                pending = row
                continue
            else:
                pending = ''

            if not row or row[0] != '~':
                continue
            elif row[1] == 'K':
                try:
                    currency_name = row[3:].split('|')[0].split('\\')[8]
                    currency = self.env['res.currency'].search([('name', '=', currency_name)], limit=1)
                    if currency:
                        budget.currency_id = currency
                except:
                    pass
            elif row[1] == 'C':
                datas = row[3:].split('|')
                code, uom, name, price, ___, ctype = datas[:6]
                ctype = int(ctype)
                if '##' in code:
                    budget.name = name or code.replace('##', '')
                    continue
                is_chapter = '#' in code
                code = code.replace('#', '')
                uom_id = uoms.get(uom, uom_obj.browse())
                concept = concept_obj.create({
                    'code': code,
                    'type': 'aux' if '%' in code else nats[ctype] if 0 < ctype < 4 else 'chapter' if is_chapter else 'departure',
                    'uom_id': uom_id.id,
                    'name': name,
                    'budget_id': budget.id,
                    'quantity': 1,
                    'amount_fixed': price,
                    'amount_type': 'fixed',
                })

                if concept.type not in ['chapter', 'departure']:
                    product = product_obj.search(['|', ('default_code', '=', code), ('barcode', '=', code)], limit=1) if self.create_all_products else self.product_id
                    if not product:
                        res_type = res_types[ctype] if ctype < 4 else None
                        product = product_obj.create({
                            'name': name,
                            'resource_type': res_type,
                            'default_code': code,
                            'type': 'product' if res_type == 'M' else 'service',
                            'list_price': price if self.product_cost_or_price == 'price' else 0,
                            'standard_price': price if self.product_cost_or_price == 'cost' else 0,
                            'categ_id': category.id,
                            'uom_id': uom_id.id or units_id,
                            'uom_po_id': uom_id.id or units_id,
                        })
                    concept.product_id = product

                concept_copies = concept_obj.browse()
                for i, (parent_code, child_data) in enumerate(children_codes.get(code, {}).items()):
                    for parent in concepts.filtered_domain([('code', '=', parent_code)]):
                        parent.amount_type = 'compute'
                        if i == 0:
                            concept.parent_id = parent
                            concept.quantity = child_data.get('qty', 0)
                            concept.sequence = child_data.get('seq', 1)
                        elif parent:
                            copy_concept = self.env.user.recursive_create(concept, parent.id, budget.id)
                            copy_concept.quantity = child_data.get('qty', 0)
                            copy_concept.sequence = child_data.get('seq', 1)
                            concept_copies += copy_concept

                concepts += concept
                # if concept_copies:
                #     concepts += concept_copies
            elif row[1] == 'D':
                datas = row[3:-1].split('|')
                parent_code = datas[0].replace('#', '')
                children = datas[1:]
                for seq, (code, __, qty) in enumerate(zip(*[iter(children[0].split('\\'))] * 3), 1):
                    qty = float(qty)
                    if code in children_codes:
                        children_codes[code][parent_code] = {'qty': qty, 'seq': seq}
                    else:
                        children_codes[code] = {parent_code: {'qty': qty, 'seq': seq}}
                    for child in concepts.filtered_domain([('code', '=', code)]) if code else concept_obj.browse():
                        for parent in concepts.filtered_domain([('code', '=', parent_code)]) if parent_code else concept_obj.browse():
                            if child.parent_id:
                                child = self.env.user.recursive_create(child, parent.id, budget.id)
                                # No se si deba meter los hijos nuevos en el total de conceptos...
                            parent.child_ids += child
                            parent.amount_type = 'compute'
                        child.sequence = seq
                        child.quantity = qty
            elif row[1] == 'M':
                datas = row[3:-1].split('|')
                __, departure_code = datas[0].split('\\')
                departure = concepts.filtered_domain([('code', '=', departure_code)])
                measuring_vals = []
                for is_formula, name, qty, length, width, height in zip(*[iter(datas[3].split('\\'))] * 6):
                    formula = formula_obj.browse()
                    if is_formula == '3':
                        formula = formula_obj.search(['|', ('formula', 'ilike', name), ('name', 'ilike', name)], limit=1)
                        if not formula:
                            # La fórmula podría fallar, así que si da problemas, no la cargamos.
                            try:
                                X = x = b = B = float(length or 0.0)
                                Y = y = c = C = float(width or 0.0)
                                Z = z = d = D = float(height or 0.0)
                                eval(name)
                                valid = True
                            except (SyntaxError, NameError):
                                valid = False
                            formula = formula_obj.create({
                                'name': name,
                                'formula': name,
                            }) if valid else formula_obj.browse()
                    if not qty:
                        self.message_post(body='Amount at 0 or null for the measurement line %d:\n%s' % (read_rows + self.last_row, row))
                    measuring_vals.append((0, 0, {
                        'space_id': default_space.id,
                        'name': name,
                        'qty': float(qty or 1.0),
                        'length': float(length or 0.0),
                        'width': float(width or 0.0),
                        'height': float(height or 0.0),
                        'amount_subtotal': float(datas[2] or 0.0),
                        'formula': formula.id,
                    }))

                departure.write({'measuring_ids': measuring_vals})
            elif row[1] == 'T':
                datas = row[3:-1].split('|')
                concept = concepts.filtered_domain([('code', '=', datas[0])])
                concept.write({'note': datas[1]})

        def rec_update(concept):
            """ Actualiza desde el último hijo hasta subir al primer padre """
            for child in concept.child_ids:
                rec_update(child)
            concept.onchange_function()
            concept.update_amount()

        for concept in budget.concept_ids:
            rec_update(concept)

        return self.write({
            'state': 'ongoing' if read_rows >= limit else 'done',
            'last_row': last_row + read_rows,
            'budget_id': budget.id,
        })

    def import_ms_xml(self):
        dt_format = '%Y-%m-%dT%H:%M:%S'
        file_content = base64.b64decode(self.excel_file)
        content = bs4.BeautifulSoup(file_content, 'lxml')
        tasks = [task for task in content.find_all('task') if task.find('wbs')]
        concept_obj = self.env['bim.concepts']
        budget = self.budget_id or self.budget_id.create({'name': 'N/A',
                                                          'project_id': self.project_id.id,
                                                          'date_end': fields.Date.today(),
                                                          'currency_id': self.project_id.currency_id.id})
        budget.do_compute = False
        concepts = budget.concept_ids
        stages_percents = {}
        for task in sorted(tasks, key=lambda t: len(t.find('wbs').text.split('.'))):
            wbs = task.find('wbs')
            if wbs and wbs.text == '0':
                continue
            if wbs and wbs.text == '1':
                budget.name = task.find('name').text
                continue
            if not wbs:
                continue
            code = (wbs.text or '').split('.')

            concept = concept_obj.create({
                'code': '.'.join(code),
                'type': 'chapter' if len(code) <= 2 else 'departure',
                'name': task.find('name').text,
                'budget_id': budget.id,
                'quantity': 1,
                'acs_date_start': datetime.datetime.strptime(task.find('start').text, dt_format),
                'acs_date_end': datetime.datetime.strptime(task.find('finish').text, dt_format),
            })

            if len(code) > 2:
                parent_code = '.'.join(code[:-1])
                parent_concept = concepts.filtered_domain([('code', '=', parent_code)])
                if len(parent_concept) == 1:
                    concept.parent_id = parent_concept

            concepts |= concept

            if self.import_stages and task.find('percentcomplete'):
                certif_percent = float(task.find('percentcomplete').text)
                if certif_percent:
                    stages_percents[concept] = certif_percent

        if self.import_stages and stages_percents:
            budget.set_estimated_dates()
            if budget.date_start and budget.date_end and budget.date_start < budget.date_end:
                budget.create_stage(1)

        if budget.stage_ids:
            budget_stage = budget.stage_ids[0]
            for concept, percent in stages_percents.items():
                concept.type_cert = 'stage'
                concept.generate_stage_list()
                stage = concept.certification_stage_ids.filtered_domain([('stage_id', '=', budget_stage.id)])
                stage.certif_percent = percent
                stage.onchange_percent()
                concept.update_amount()

        return self.write({
            'state': 'done',
            'budget_id': budget.id,
        })


class BimImportWizard(models.TransientModel):
    _name = 'bim.import.wizard'
    _description = 'Project Importer'

    version = fields.Selection([('8.8', 'Excel Template'), ('bc3', 'BC3'), ('ms_xml', 'Project XML')], 'Version', default='8.8', required=True)
    project_id = fields.Many2one('bim.project', 'Project', required=True)
    create_all_products = fields.Boolean('Create non-existent products')
    product_id = fields.Many2one('product.product', 'Default product', default=lambda self: self.env.ref('base_bim_2.default_product', raise_if_not_found=False))
    excel_file = fields.Binary('Excel file', required=True)
    filename = fields.Char('File name')
    product_cost_or_price = fields.Selection([('price', 'Sale Price'), ('cost', 'Product Cost')],
                                             string='Assign to', default='cost')
    import_stages = fields.Boolean()

    def import_data(self):
        self.env['bim.import.temp'].create({
            'version': self.version,
            'project_id': self.project_id.id,
            'create_all_products': self.create_all_products,
            'product_id': self.product_id.id,
            'excel_file': self.excel_file,
            'filename': self.filename,
            'import_stages': self.import_stages,
            'product_cost_or_price': self.product_cost_or_price,
        })
        return {'type': 'ir.actions.act_window_close'}


def rindex(alist, val):
    return len(alist) - alist[-1::-1].index(val) - 1
