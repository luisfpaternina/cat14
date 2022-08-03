# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _

class ProjectTask(models.Model):

    _inherit = 'project.task'

    stock_picking_ids = fields.Many2many(
        'stock.picking',
        string="Material request",
        compute="compute_picking_ids")

    def compute_picking_ids(self):
        for record in self:
            pickigns = self.env['stock.picking'].search([('task_id','=',self.id)])
            if pickigns:
                record.stock_picking_ids = pickigns.ids
            else:
                record.stock_picking_ids = False
