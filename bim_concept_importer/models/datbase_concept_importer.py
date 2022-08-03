# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DatabaseConceptImporter(models.Model):
    _description = "Database Concept Importer"
    _name = 'database.concept.importer'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    name = fields.Char('Code', copy=False)
    title = fields.Char('Title')
    obs = fields.Text('Obs')
    project_ids = fields.Many2many('bim.project')

    line_ids = fields.One2many(
        'database.concept.importer.line', 'database_concept_importer_id', string='Database Concept Importer Line')


class DatabaseConceptImporterLine(models.Model):
    _name = 'database.concept.importer.line'
    _description = 'Database Concept Importer Line'

    product_id = fields.Many2one(
        'product.product', 'Product')
    qty = fields.Float('Quantity', default=1)

    database_concept_importer_id = fields.Many2one(
        'database.concept.importer', 'Database Concept Importer', ondelete='cascade')