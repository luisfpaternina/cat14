# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleSuscriptionDemand(models.Model):
    _name = 'sale.subscription.demand'
    _inherit = 'mail.thread'
    _description = 'Demands'
    _rec_name = 'code'

    name = fields.Char(
        string="Name",
        tracking=True)
    code = fields.Char(
        string="Demand number",
        tracking=True)
    date = fields.Date(
        string="Date",
        tracking=True)
    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        tracking=True)
    street = fields.Char(
        related="partner_id.street",
        string="Address")
    phone = fields.Char(
        related="partner_id.mobile",
        string="Phone")
    email = fields.Char(
        string="Email",
        related="partner_id.email")
    state_id = fields.Many2one(
        'res.country.state',
        string="State",
        related="partner_id.state_id")
    city = fields.Char(
        string="Population",
        related="partner_id.city")
    is_embargo = fields.Boolean(
        string="Embargo",
        tracking=True)
    observations = fields.Text(
        string="Observations",
        tracking=True)
    notes = fields.Text(
        string="Notes",
        tracking=True)
    demand_line_ids = fields.One2many(
        'subscription.demand.amount',
        'demand_id',
        string="Amounts")
    subscription_type_id = fields.Many2one(
        'stock.gadgets.contract.type',
        string="Subscription type",
        tracking=True)
    reason_change_id = fields.Many2one(
        'subscription.reason.change',
        string="Reason change",
        tracking=True)
    inspection_report_id = fields.Many2one(
        'subscription.inspection.report',
        string="Inspection report",
        tracking=True)
    is_claim = fields.Boolean(
        string="Claim",
        tracking=True)
    claim_date = fields.Date(
        string="Claim date",
        tracking=True)
    reception_date = fields.Date(
        string="Reception date",
        tracking=True)
    delivery_name = fields.Char(
        string="Delivery name",
        tracking=True)
    telephone = fields.Char(
        string="Telephone",
        tracking=True)
    is_compensation = fields.Boolean(
        string="Compensation",
        tracking=True)
    trimester = fields.Char(
        string="Trimester",
        tracking=True)
    imp_trimester = fields.Float(
        string="Imp.Trimestal",
        tracking=True)
    compensation_total = fields.Float(
        string="Total compensation",
        tracking=True)
    is_demand = fields.Boolean(
        string="Is demand",
        tracking=True)
    partner_demand_id = fields.Many2one(
        'res.partner',
        string="Demand partner",
        tracking=True)
    court_number = fields.Char(
        string="Court number",
        tracking=True)
    process_id = fields.Many2one(
        'subscription.process',
        string="Process",
        tracking=True)
    is_powers = fields.Boolean(
        string="Powers",
        tracking=True)
    partner_president_id = fields.Many2one(
        'res.partner',
        string="President",
        tracking=True)
    president_phone = fields.Char(
        string="President phone",
        related="partner_president_id.phone")
    trial_citation = fields.Datetime(
        string="Trial citation",
        tracking=True)
    partner_lawyer_id = fields.Many2one(
        'res.partner',
        string="Lawyer",
        tracking=True)
    partner_attorney_id = fields.Many2one(
        'res.partner',
        string="Attorney",
        tracking=True)
    is_failure = fields.Boolean(
        string="Is failure")
    sentence_number = fields.Char(
        string="Sentence number")
    sentence_date = fields.Date(
        string="Sentence date")
    end_payment = fields.Date(
        string="End payment")
    is_appeal = fields.Boolean(
        string="Is appeal")
    appeal_date = fields.Date(
        string="Appeal date")
    is_settlement = fields.Boolean(
        string="Is settlement")
    settlement_date = fields.Date(
        string="Settlement date")
