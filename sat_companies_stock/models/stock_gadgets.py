# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime

class StockGadgets(models.Model):
    _name = 'stock.gadgets'
    _inherit = 'mail.thread'
    _description = 'Gadgets'
    _rec_name = 'code'

    code = fields.Char(
        string="Code",
        tracking=True,
        readonly=True,
        required=True,
        copy=False,
        default='New')
    domicile = fields.Char(
        string="Domicile",
        tracking=True)
    ref_type = fields.Char(
        string="Type",
        tracking=True)
    inspection_date = fields.Date(
        string="Last inspection date",
        tracking=True)
    next_inspection_date = fields.Date(
        string="next inspection date",
        tracking=True)
    pending_date_corrected = fields.Date(
        string="Pending date to be corrected",
        tracking=True)
    correction_date = fields.Date(
        string="Date of correction",
        tracking=True)
    years = fields.Selection([
        ('two','2 years'),
        ('four','4 years'),
        ('six','6 years')],string="Years",tracking=True)
    use = fields.Char(string="Use")
    state_gadget = fields.Char(string="State")
    type_contract = fields.Selection([
        ('normal','Normal'),
        ('all_risk','All risk')],string="Type of contract",tracking=True)
    type_assistance = fields.Char(
        string="Type assistance",
        tracking=True)
    is_priority = fields.Boolean(
        string="Is priority",
        tracking=True)
    is_full_service = fields.Boolean(
        string="Is 24H",
        tracking=True)
    keys = fields.Char(
        string="Keys",
        tracking=True)
    edifice = fields.Char(
        string="Edifice",
        tracking=True)
    high_date_call_center = fields.Date(
        string="High date call center",
        tracking=True)
    population_id = fields.Many2one(
        'res.partner.population',
        string="Population",
        tracking=True)
    user_id = fields.Many2one(
        'res.users',
        string="Admin",
        tracking=True)
    location = fields.Char(
        string="Location",
        tracking=True)
    type_gadget = fields.Char(
        string="Type",
        tracking=True)
    high_date = fields.Date(
        string="High date",
        tracking=True)
    end_guarantee = fields.Date(
        string="End guarantee",
        tracking=True)
    end_date_contract = fields.Date(
        string="End date contract",
        tracking=True)
    start_date_contract = fields.Date(
        string="Start contract date",
        tracking=True)
    high_mto_company = fields.Char(
        string="High Mto company",
        tracking=True)
    contract_number = fields.Char(
        string="N° contract",
        tracking=True)
    invoice_start_date = fields.Date(
        string="Invoice start date",
        tracking=True)
    years_extended = fields.Integer(
        string="Years of extended",
        tracking=True)
    extended_date = fields.Date(
        string="Extended date",
        tracking=True)
    start_up_date = fields.Date(
        string="Start up date",
        tracking=True)
    low_date = fields.Date(
        string="Low date",
        tracking=True)
    low_mto_company = fields.Char(
        string="Low Mto company",
        tracking=True)
    billing_period  = fields.Char(
        string="Billing period",
        tracking=True)
    type_increase = fields.Char(
        string="Type of increase",
        tracking=True)
    gadget_state = fields.Selection([
        ('active','Activo'),
        ('unsubscribe','Unsubscribe')],string="Gadget state", default="active")
    gadget_state_id = fields.Many2one(
        'stock.gadgets.state',
        string="State",
        tracking=True)
    gadget_type_assistance_id = fields.Many2one(
        'stock.gadgets.types.assistance',
        string="Type assistance",
        tracking=True)
    type_contract_id = fields.Many2one(
        'stock.gadgets.contract.type',
        string="Contract type",
        tracking=True)
    ref = fields.Char(
        string="Reference",
        tracking=True)
    name = fields.Char(
        string="Name",
        tracking=True)
    address = fields.Char(
        string="Address",
        tracking=True)
    address2 = fields.Char(
        string="Address 2",
        tracking=True)
    address3 = fields.Char(
        string="Address 3",
        tracking=True)
    assistance_type_id = fields.Many2one(
        'stock.gadgets.types.assistance',
        string="Assistance type",
        tracking=True)
    increse_type_id = fields.Many2one(
        'stock.gadgets.increase.type',
        string="Increse type",
        tracking=True)
    billing_period_id = fields.Many2one(
        'stock.gadgets.billing.period',
        string="Billing period",
        tracking=True)
    billing_period_name = fields.Char(
        string="Name billing period",
        related="billing_period_id.name")
    increse_type_name = fields.Char(
        string="Name increase",
        related="increse_type_id.name")
    population_name = fields.Char(
        string="Population name",
        related="population_id.name")
    years_number = fields.Integer(
        string="Years",
        tracking=True)
    months_number = fields.Integer(
        string="Months",
        tracking=True)
    partner_admin_id = fields.Many2one(
        'res.partner',
        string="Admin",
        tracking=True)
    res_partner_high_mto_id = fields.Many2one(
        'res.partner',
        string="High Mto company",
        tracking=True)
    res_partner_low_mto_id = fields.Many2one(
        'res.partner',
        string="Low Mto company",
        tracking=True)
    gadget_use_id = fields.Many2one(
        'stock.gadgets.use',
        string="Use")


    # Ejecutar Secuencia 
    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('gadgets') or 'New'
        result = super(StockGadgets, self).create(vals)
        return result


    @api.constrains('start_date_contract','end_date_contract')
    def validate_contracs_dates(self):
        if self.start_date_contract > self.end_date_contract:
            raise ValidationError(_(
                'The contract start date cannot be greater than the end date'))
