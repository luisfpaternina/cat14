# -*- coding: utf-8 -*-
import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from pytz import timezone

class SaleSuscriptionTemplateInherit(models.Model):
    _inherit = 'sale.subscription.template'

    sale_type_id = fields.Many2one(
        'sale.order.type',
        string="Sale type")
    type_contract = fields.Selection([
        ('normal','Normal'),
        ('risk','All risk')],string="Type of contract",tracking=True)
    gadgets_contract_type_id = fields.Many2one(
        'stock.gadgets.contract.type',
        string="Subscription type")
    jan = fields.Boolean(
        'January')
    feb = fields.Boolean(
        'February')
    mar = fields.Boolean(
        'March')
    apr = fields.Boolean(
        'April')
    may = fields.Boolean(
        'May')
    jun = fields.Boolean(
        'June')
    jul = fields.Boolean(
        'July')
    aug = fields.Boolean(
        'Auguts')
    sep = fields.Boolean(
        'September')
    oct = fields.Boolean(
        'October')
    nov = fields.Boolean(
        'November')
    dec = fields.Boolean(
        'December')
    days_number = fields.Integer(
        string="Days number")
    days_between_visits = fields.Integer(
        string="Days between visits")
    contract_duration = fields.Integer(
        string="Contract duration")
    contract_recurring_rule = fields.Selection([
        ('days','Days'),
        ('months','Months'),
        ('years','Years')],string="Contract recurring rule")
    udn_id = fields.Many2one(
        'project.task.categ.udn',
        string="Udn")
    
    @api.onchange('sale_type_id')
    def domain_udns(self):
    # FUNCIÓN PARA APLICAR DOMINIO
        for record in self:
            if record.sale_type_id:
                return {'domain': {'udn_id': [('ot_type_id', '=', record.sale_type_id.id)]}}
            else:
                return {'domain': {'udn_id': []}}
