# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderTemplateInherit(models.Model):
    _inherit = 'sale.order.template'

    sale_type_id = fields.Many2one(
        'sale.order.type',
        string="Sale type")
    type_contract = fields.Selection([
        ('normal','Normal'),
        ('risk','All risk')],string="Type of contract")
    gadgets_contract_type_id = fields.Many2one(
        'stock.gadgets.contract.type')
    udn_id = fields.Many2one(
        'project.task.categ.udn',
        string="Udn")
    is_maintenance = fields.Boolean(
        string="Is maintenance",
        related="sale_type_id.is_maintenance")
    

    @api.onchange('sale_type_id')
    def domain_saletype_udn(self):
        for record in self:
            if record.sale_type_id:
                return {'domain': {'udn_id': [('ot_type_id', '=', record.sale_type_id.id)]}}
            else:
                return {'domain': {'udn_id': []}}
