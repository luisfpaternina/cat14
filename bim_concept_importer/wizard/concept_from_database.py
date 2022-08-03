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

class ConceptFromDatabase(models.TransientModel):
    _name = "concept.from.database.wizard"
    _description = "Wizard Concept From Database"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['budget_id'] = self._context.get('active_id', False)
        return res

    budget_id = fields.Many2one('bim.budget')
    price_type = fields.Selection([
        ('comp_price', 'Price Components'),
        ('conc_price', 'Concepts Price'),
        ], string="Price Type", default='comp_price')
    replace_concepts = fields.Boolean(default=True)
    budget_cost_list_id = fields.Many2one('bim.cost.list', related='budget_id.cost_list_id', readonly=False)
    use_cost_list = fields.Boolean(related='budget_id.use_cost_list')

    def action_process_database(self):
        concept_bd_obj = self.env['database.concept.importer']
        concept_obj = self.env['bim.concepts']
        type_work = self.budget_id.company_id.type_work
        for concept in self.budget_id.concept_ids.filtered_domain([('type','=','departure')]):
            possible_db = concept_bd_obj.search([('name','=',concept.code)], limit=1)
            created_concepts = []
            if (possible_db and not possible_db.project_ids) or (possible_db and self.budget_id.project_id in possible_db.project_ids):
                if self.replace_concepts:
                    for child in concept.child_ids.filtered_domain([('type','in',['labor','equip','material'])]):
                        child.unlink()
                last_code = len(concept.child_ids)
                product_qty = 0
                for line in possible_db.line_ids:
                    if line.product_id.resource_type in ['M','H','Q']:
                        if line.product_id.resource_type == 'H':
                            concept_type = 'labor'
                        elif line.product_id.resource_type == 'M':
                            concept_type = 'material'
                        else:
                            concept_type = 'equip'
                        last_code += 1
                        product_qty += line.qty
                        if self.price_type == 'comp_price':
                            price = line.product_id.standard_price
                            if type_work == 'price':
                                price = line.product_id.list_price
                            elif type_work == 'pricelist' and self.budget_id.pricelist_id:
                                price = self.budget_id.pricelist_id.get_product_price(line.product_id, line.qty, self.budget_id.project_id.customer_id,
                                                                    uom_id=line.product_id.uom_id.id)
                            elif type_work == 'costlist' and self.budget_cost_list_id and self.use_cost_list:
                                price = self.budget_cost_list_id._get_product_bim_cost_list(line.product_id)
                                if not price:
                                    price = line.product_id.standard_price
                        else:
                            price = 0

                        new_concept = concept_obj.create({
                            'product_id': line.product_id.id,
                            'parent_id': concept.id,
                            'code': concept.code +'.'+ str(last_code),
                            'budget_id': self.budget_id.id,
                            'name': line.product_id.display_name,
                            'type': concept_type,
                            'uom_id': line.product_id.uom_id.id,
                            'amount_fixed': price,
                            'quantity': line.qty
                        })
                        created_concepts.append(new_concept)
                if self.price_type == 'conc_price':
                    for new_cp in created_concepts:
                        factor = new_cp.quantity / product_qty
                        concept_amount = concept.amount_fixed
                        balance = factor * concept_amount
                        new_cp.balance = balance
                        new_cp.amount_fixed = balance / new_cp.quantity
                concept.amount_type = 'compute'
