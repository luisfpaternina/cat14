# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    task_id = fields.Many2one(
        'project.task',
        string="Task")
    gadget_id = fields.Many2one(
        'product.template',
        string="Gadget",
        related="task_id.product_id")


    @api.onchange('task_id')
    def get_partner_id_from_task(self):
    # FUNCIÓN PARA RELACIONAR CONTACTO DE LA OT
        for rec in self:
            if rec.task_id:
                rec.partner_id = rec.task_id.partner_id.id
            else:
                rec.partner_id = False
  