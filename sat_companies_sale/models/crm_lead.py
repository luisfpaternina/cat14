# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    is_external = fields.Boolean(
        string="Is external",
        tracking=True,
        compute="_compute_is_external")
    sale_type_id = fields.Many2one(
        'sale.order.type',
        string="Sale type",
        tracking=True)
    oportunity_type_id = fields.Many2one(
        'crm.lead.type',
        string="Oportunity type",
        related="stage_id.oportunity_type_id")
    client_type = fields.Selection(
        [('neighborhood_community','Neighborhood community'),
        ('companies','Companies/builders'),
        ('public_organisms','Public organisms'),
        ('family_home','Single-family private homes')],string="Client type")
    managed_by = fields.Selection([
        ('president','President'),
        ('admin','Administrator')],string="Managed by")
    is_medium_website = fields.Boolean(
        string="Website medium",
        compute="_compute_check_medium_id")
    is_medium_email = fields.Boolean(
        string="Email medium",
        compute="_compute_check_email_medium_id")
    partner_admin_id = fields.Many2one(
        'res.partner',
        string="Farm administrator")
    quote_date_sent_min = fields.Date(
        string="Quote date sent min",
        compute="_compute_quote_date_sent_min")
    opportunity_days = fields.Integer(
        string="Opportunity days",
        compute="_calculated_days")
    stage_days = fields.Integer(
        string="Stage days",
        related="oportunity_type_id.days_maximum_stage")
    int_opportunity_days = fields.Integer(
        string="Int opportunity days")
    int_stage_days = fields.Integer(
        string="Int stage days")
    is_validate_days = fields.Boolean(
        string="Validate days")
    udn_type_id = fields.Many2one(
        'project.task.categ.udn',
        string="Udn")
    tracing_ids = fields.One2many(
        'crm.lead.tracing',
        'lead_id',
        string="Tracing")
    expected_revenue = fields.Monetary(
        string="Expected revenue",
        compute="_compute_expected_revenue",
        store=True)
    expected_total = fields.Float(
        string="Expected total",
        compute="_compute_expected_revenue")
    is_low = fields.Boolean(
        string="Is low",
        related="partner_id.is_low")
    
    
    @api.depends('order_ids')
    def _compute_expected_revenue(self):
        if self.order_ids:
            lista = []
            for line in self.order_ids:
                lista.append(line.amount_total)
                total = sum(lista)
                self.expected_total = total
                self.expected_revenue = total
        else:
            print("Oportunidad no tiene presupuestos")
            self.expected_total = 0
            self.expected_revenue = 0

    @api.onchange('sale_type_id')
    def domain_saletype_udn(self):
        for record in self:
            if record.sale_type_id:
                return {'domain': {'udn_type_id': [('ot_type_id', '=', record.sale_type_id.id)]}}
            else:
                return {'domain': {'udn_type_id': []}}

    @api.onchange(
        'stage_id',
        'oportunity_type_id',
        'quote_date_sent_min',
        'name')
    def _validate_days(self):
        if self.opportunity_days > self.stage_days:
            self.is_validate_days = True
        return False

    @api.depends('medium_id')
    def _compute_check_medium_id(self):
        for record in self:
            record.is_medium_website = True if record.medium_id and record.medium_id[0].name  == 'Website' else False

    @api.depends('medium_id')
    def _compute_check_email_medium_id(self):
        for record in self:
            record.is_medium_email = True if record.medium_id and record.medium_id[0].name  == 'Email' else False

    @api.depends('medium_id')
    def _compute_is_external(self):
        for record in self:
            if record.is_medium_email == True or record.is_medium_website == True:
                record.is_external = True
            else:
                record.is_external = False

    def _compute_quote_date_sent_min(self):
        for record in self:
            dt_orders = []
            min_date = False
            for line in record.order_ids:
                if line.quote_date_sent:
                    dt_orders.append(line.quote_date_sent)
            if dt_orders:
                min_date = min(dt_orders)
                max_date = max(dt_orders)
            record.quote_date_sent_min = min_date

    @api.depends('quote_date_sent_min')
    def _calculated_days(self):
        today = date.today()
        for record in self:
            if record.quote_date_sent_min:
                record.opportunity_days = (today - record.quote_date_sent_min).days
            else:
                record.opportunity_days = 0

    def action_new_quotation(self):
        result = super(CrmLead, self).action_new_quotation()
        if result.get('id'):
            vals = {
                'default_udn_id': self.udn_type_id.id,
                'default_sale_type_id': self.sale_type_id.id,
            }
            result.get('context').update(vals)
        return result
