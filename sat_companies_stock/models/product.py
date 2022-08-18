# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .qr_code_base import generate_qr_code
import base64
from io import BytesIO
import qrcode
from datetime import datetime
from datetime import date
import logging


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    zone_id = fields.Many2one(
        'res.partner.zones',
        string="Zone",
        tracking=True)
    zone_name = fields.Char(
        string="Zone name",
        related="zone_id.name")
    gadget_id = fields.Many2one(
        'stock.gadgets',
        string="Gadget",
        tracking=True)
    code = fields.Char(
        string="Code",
        tracking=True)
    domicile = fields.Char(
        string="Domicile",
        tracking=True)
    ref_type = fields.Char(
        string="Ref type",
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
        ('six','6 years')],string="Total Years",tracking=True)
    use = fields.Char(string="Used")
    state_gadget = fields.Char(string="State test")
    type_contract = fields.Selection([
        ('normal','Normal'),
        ('all_risk','All risk')],string="Contract",tracking=True)
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
        string="Date population",
        tracking=True)
    user_id = fields.Many2one(
        'res.users',
        string="Admin user",
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
        string="High Mto",
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
        string="Low Mto",
        tracking=True)
    billing_period  = fields.Char(
        string="Billing",
        tracking=True)
    type_increase = fields.Char(
        string="Increase",
        tracking=True)
    gadget_state = fields.Selection([
        ('active','Activo'),
        ('unsubscribe','Unsubscribe')],string="Validate active", default="active")
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
        tracking=True,
        related="partner_admin_id.street")
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
    is_gadget = fields.Boolean(
        string="Is gadget",
        tracking=True)
    city = fields.Char(
        string="Population",
        related="partner_id.city")
    partner_zip = fields.Char(
        string="Postal code",
        related="partner_id.zip")
    cabine_phone = fields.Char(
        string="Cabine phone",
        tracking=True)
    latitude = fields.Float(
        string="Latitude",
        tracking=True,
        digits=(12,7))
    length = fields.Float(
        string="Length",
        tracking=True,
        digits=(12,7))
    route_id = fields.Many2one(
        'res.partner.routes',
        string="Route",
        tracking=True)
    route_name = fields.Char(
        string="Route name",
        related="route_id.name")
    partner_oca_id = fields.Many2one(
        'res.partner',
        string="OCA")
    is_january = fields.Boolean(
        string="January")
    is_february = fields.Boolean(
        string="February")
    is_march = fields.Boolean(
        string="March")
    is_april = fields.Boolean(
        string="April")
    is_may = fields.Boolean(
        string="May")
    is_june = fields.Boolean(
        string="June")
    is_july = fields.Boolean(
        string="July")
    is_august = fields.Boolean(
        string="August")
    is_september = fields.Boolean(
        string="September")
    is_october = fields.Boolean(
        string="October")
    is_november = fields.Boolean(
        string="November")
    is_december = fields.Boolean(
        string="December")
    delegation_id = fields.Many2one(
        'res.partner.delegation',
        string="Delegation",
        related="zone_id.delegation_id")
    delegation_name = fields.Char(
        string="Delegation name",
        related="delegation_id.name")
    rae = fields.Char(
        string="R.A.E.",
        tracking=True)
    last_inspection = fields.Date(
        string="Last inspection")
    next_inspection = fields.Date(
        string="Next inspection")
    years_inspection = fields.Integer(
        string="Inspection years")
    maintenance_frequency_id = fields.Many2one(
        'stock.maintenance.frequency',
        string="Maintenance frequency")
    frequency_name = fields.Char(
        string="Frequency name",
        related="maintenance_frequency_id.name")
    planning_type_id = fields.Many2one(
        'stock.planning.type',
        string="Planning type")
    planning_type_name = fields.Char(
        string="Planning type name")
    employee_notice_id = fields.Many2one(
        'hr.employee',
        string="Operator notice",
        related="zone_id.employee_id",
        tracking=True)
    employee_greasing_id = fields.Many2one(
        'hr.employee',
        string="Greasing operator",
        related="zone_id.employee_greasing_id",
        tracking=True)
    responsable_zone_id = fields.Many2one(
        'hr.employee',
        related="zone_id.responsable_id")
    elevator_type_id = fields.Many2one(
        'stock.elevator.type',
        string="Elevator type")
    is_machine_room = fields.Boolean(
        string="Machine room")
    gadget_model = fields.Char(
        string="Gadget model")
    partner_maker_id = fields.Many2one(
        'res.partner',
        string="Maker")
    tractor_group = fields.Char(
        string="Tractor group")
    landing_doors_id = fields.Many2one(
        'stock.landing.doors',
        string="Landing doors")
    company_product_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id)
    model_gadget = fields.Char(
        string="Model gadget")
    bench_id = fields.Many2one(
        'stock.bench',
        string="Bench")
    motor_power = fields.Char(
        string="Motor power(KW)")
    engine_brake = fields.Char(
        string="Engine brake")
    stop_numbers = fields.Char(
        string="Stops numbers")
    people_numbers = fields.Char(
        string="People numbers")
    gadget_load = fields.Char(
        string="Load(Kgs)")
    nominal_speed = fields.Char(
        string="Nominal speed(m/s)")
    route = fields.Char(
        string="Route of gadget")
    reduced_pit = fields.Boolean(
        string="Reduced pit")
    reduced_flight = fields.Boolean(
        string="Reduced flight")
    gate_operator = fields.Char(
        string="Gate operator")
    shipment_id = fields.Many2one(
        'stock.shipment',
        string="Shipment")
    soil_type_id = fields.Many2one(
        'stock.soil.type',
        string="Soil type")
    cockpit_type_id = fields.Many2one(
        'stock.cockpit.type',
        string="Cockpit type")
    cockpit_push_type_id = fields.Many2one(
        'stock.cockpit.push.type',
        string="Cockpit push type")
    wash_cabin_id = fields.Many2one(
        'stock.wash.cabin',
        string="Wash cabin")
    is_weigher = fields.Boolean(
        string="Is weigher")
    landing_doors_id = fields.Many2one(
        'stock.landing.doors',
        string="Landing doors")
    landing_keypad_id = fields.Many2one(
        'stock.landing.keypad',
        string="Landing keypad")
    landing_lock_id = fields.Many2one(
        'stock.landing.lock',
        string="Landing lock type")
    landing_key_id = fields.Many2one(
        'stock.landing.key',
        string="Landing key")
    traction_cables = fields.Char(
        string="Traction cables")
    maneuver = fields.Char(
        string="Maneuver")
    maneuvering_table_id = fields.Many2one(
        'stock.maneuvering.table',
        string="Maneuvering table")
    operator_strap = fields.Char(
        string="Operator strap")
    is_operator_brake = fields.Boolean(
        string="Is operator brake")
    is_cabin_timed_light = fields.Boolean(
        string="Is cabin timed light")
    cabin_tubes_type_id = fields.Many2one(
        'stock.types.cabin.tubes',
        string="Cabin tubes types")
    traction_pulley = fields.Char(
        string="Traction pulley(cm)")
    tensioner_pulley = fields.Char(
        string="Tensioner pulley(cm)")
    limiter_pulley = fields.Char(
        string="Limiter pulley(cm)")
    deflection_pulley = fields.Char(
        string="Deflection pulley(cm)")
    is_wedging_cabin = fields.Boolean(
        string="Is wedging cabin")
    is_counterweight_wedging = fields.Boolean(
        string="Is counterweight wedging")
    is_cabin_puffer = fields.Boolean(
        string="Is cabin puffer")
    is_counterweight_puffer = fields.Boolean(
        string="Is counterweight puffer")
    bidirectional_model_id = fields.Many2one(
        'stock.bidirectional.model',
        string="Bidirectional model")
    counterweight_pulley = fields.Char(
        string="Counterweight pulley(cm)")
    gsm_model_id = fields.Many2one(
        'stock.gsm.model',
        string="GSM model")
    line = fields.Selection([
        ('1','Fija'),
        ('2','Movil')],string="Line")
    is_netel_line = fields.Boolean(
        string="Is netel line")
    tension = fields.Integer(
        string="Tension")
    qr_pit = fields.Binary(
        'Dowload Qr Image Pit',
        compute="_generate_qr_code")
    qr_pit_image = fields.Binary(
        'QR CODE IMAGE PIT',
        compute="_generate_qr_code")
    qr_cabine = fields.Binary(
        'Dowload QR Image Cabine',
        compute="_generate_qr_code")
    qr_cabine_image = fields.Binary(
        'QR CODE IMAGE CABINE',
        compute="_generate_qr_code")
    qr_machine = fields.Binary(
        'Dowload QR Image Machine',
        compute="_generate_qr_code")
    qr_machine_image = fields.Binary(
        'QR CODE IMAGE MACHINE',
        compute="_generate_qr_code")
    is_festive = fields.Boolean(
        string="Festive")
    state_record_id = fields.Many2one(
        'stock.state.record',
        string="State record",
        tracking=True)
    is_validate_date = fields.Boolean(
        string="Validate dates",
        compute="_validate_low_date")
    today = fields.Date(
        string="Today",
        default=fields.Date().today())
    active_name = fields.Char(
        string="Active name",
        compute="_active_product")
    partner_type_id = fields.Many2one(
        'res.partner.type',
        string="Partner type")
    is_community = fields.Boolean(
        string="Is community")
    photo1 = fields.Binary(
        string="Photo 1")
    photo2 = fields.Binary(
        string="Photo 2")
    photo3 = fields.Binary(
        string="Photo 3")
    gadget_high_date = fields.Date(
        string="Gadget high date")
    gadget_low_date = fields.Date(
        string="Gadget low date")
    has_rae = fields.Boolean(
        string="Has RAE",
        compute="compute_rae")
    there_are_keys = fields.Boolean(
        string="There are keys")
    number_of_tubes = fields.Char(
        string="Number of tubes")
    is_good_points = fields.Boolean(
        string="Good points")
    end_date_correction =fields.Date(
        string="End date correction")
    user_inps_id = fields.Many2one(
        'res.users',
        string="Operator inps")
    gadget_population = fields.Char(
        string="Gadget population")
    is_recurring_task = fields.Boolean(
        string="Recurring")
    repeat_interval = fields.Integer(
        string="Repeat interval")
    repeat_unit = fields.Selection([
        ('day','Days'),
        ('week','Weeks'),
        ('month','Months'),
        ('year','Years')],string="Repeat unit")
    repeat_until = fields.Date(string="End Date")
    repeat_number = fields.Integer(string="Repetitions")
    mon = fields.Boolean(
        string="Monday")
    tue = fields.Boolean(
        string="Tuesday")
    wed = fields.Boolean(
        string="Wednesday")
    thu = fields.Boolean(
        string="Thursday")
    fri = fields.Boolean(
        string="Friday")
    sat = fields.Boolean(
        string="Saturday")
    sun = fields.Boolean(
        string="Sunday")
    repeat_on_year = fields.Selection([
        ('date','Date'),
        ('day','Day')],string="Repeat year")
    repeat_on_month = fields.Selection([
        ('date','Date'),
        ('day','Day')],string="Repeat year")
    repeat_month = fields.Selection([
        ('january','January'),
        ('february','February'),
        ('march','March'),
        ('april','April'),
        ('may','May'),
        ('june','June'),
        ('july','July'),
        ('august','August'),
        ('september','September'),
        ('october','October'),
        ('november','November'),
        ('december','December')],string="Repeat month")
    repeat_weekday = fields.Selection([
        ('mon','Monday'),
        ('tue','Tuesday'),
        ('wed','Wednesday'),
        ('thu','Thursday'),
        ('fri','Friday'),
        ('sat','Saturday'),
        ('sun','Sunday')],string="Repeat weekday")
    repeat_type = fields.Selection([
        ('forever','Forever'),
        ('until','Until'),
        ('after','Repeat number')],string="Repeat type")
    repeat_show_day = fields.Boolean(
        string="Repeat show day")
    repeat_show_dow = fields.Boolean(
        string="Repeat show dow")
    repeat_show_week = fields.Boolean(
        string="Repeat show week")
    repeat_show_month = fields.Boolean(
        string="Repeat show month")
    inspection_type_id = fields.Many2one(
        'stock.inspection.type',
        string="Inspection type")
    correction_period = fields.Char(
        string="Correction period")
    correction_period_date = fields.Date(
        string="Correction period date")
    date_pending_correction = fields.Date(
        string="Date pending correction")
    bad_points = fields.Boolean(
        string="Bad points")
    is_conflictivea_pparatus = fields.Boolean(
        string="Is conflictive apparatus",
        compute="compute_is_conflictive_gadgets")
    is_second_hand = fields.Boolean(
        string="Is second hand")
    product_tag_id = fields.Many2many(
        'stock.product.tags',
        string="Tags")
    is_gadget_stopped = fields.Boolean(
        string="Is gadget stopped",
        tracking=True)
    stop_reason_id = fields.Many2one(
        'gadget.stop.reason',
        string="Reason",
        tracking=True)
    ots_id = fields.Many2many(
        'project.task',
        string="OTs",
        compute="compute_ots_in_gadgets")


    def compute_ots_in_gadgets(self):
        for record in self:
            ots = self.env['project.task'].search([('product_id','=',self.id),('is_warning','=', True)])
            if ots:
                record.ots_id= ots.ids
            else:
                record.ots_id = False
    
    def compute_is_conflictive_gadgets(self):
    # VALIDAR SI UN APARATO ES CONFLICTIVO
        values = []
        repeat = []
        unique = []
        resultSum = 0
        ots = self.env['project.task'].search([('product_id','=',self.id),('is_warning','=', True)])
        for o in ots:
            month = o.create_date.month
            values.append(month)
        for i in values:
            if i not in unique:
                unique.append(i)
            else:
                resultSum += i
                if i not in repeat:
                    repeat.append(i)
        print("Los valores que se repiten son:", repeat)
        if len(self.ots_id) >= 2 and resultSum > 0:
            self.write({'is_conflictivea_pparatus': True})
        else:
            self.is_conflictivea_pparatus = False

    def not_gadget_stopped(self):
        for record in self:
            if record.is_gadget_stopped:
                record.write({'is_gadget_stopped': False})

    def action_done_show_wizard(self):
       return {'type': 'ir.actions.act_window',
               'name': _('Gadget stopped reason'),
               'res_model': 'product.stopped.wizard',
               'target': 'new',
               'view_id': self.env.ref('sat_companies_stock.product_stopped_wizard_form').id,
               'view_mode': 'form',
               'context': {}
               }
    
    @api.depends('is_gadget')
    def compute_rae(self):
        if self.is_gadget:
            has_rae = self.env['ir.config_parameter'].sudo().get_param('sat_companies.has_rae') or False
            self.has_rae = has_rae
        else:
            self.has_rae = False

    @api.onchange('is_gadget')
    def _onchange_is_gadget(self):
        for record in self:
            if record.is_gadget == True:
                record.type = 'service'
                record.purchase_ok = False

    @api.onchange('partner_id')
    def _onchange_partner_admin_id(self):
        if self.partner_id:
            self.is_community = self.partner_id.is_community
        else:
            self.is_community = False

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_type_id = self.partner_id.partner_type_id
        else:
            self.partner_type_id = False

    @api.depends('gadget_low_date')
    def _validate_low_date(self):
        for record in self:
            if record.gadget_low_date:
                if date.today() > record.gadget_low_date:
                    record.is_validate_date = True
                else:
                    record.is_validate_date = False
            else:
                record.is_validate_date = False

    @api.onchange('gadget_low_date','is_validate_date')
    def _active_product(self):
        for record in self:
            if record.is_validate_date:
                record.active = False
                record.active_name = 'BAJA'
            else:
                record.active = True
                record.active_name = 'ALTA'

    def _generate_qr_code(self):
        for record in self:
            if record.is_gadget == True:
                base_url_pit = "pit,%d" % (record.id)
                base_url_cabine = "cabine,%d" % (record.id)
                base_url_machine = "machine,%d" % (record.id)
                record.qr_pit = generate_qr_code(base_url_pit)
                record.qr_pit_image = generate_qr_code(base_url_pit)
                record.qr_cabine = generate_qr_code(base_url_cabine)
                record.qr_cabine_image = generate_qr_code(base_url_cabine)
                record.qr_machine = generate_qr_code(base_url_machine)
                record.qr_machine_image = generate_qr_code(base_url_machine)
            else:
                record.qr_pit = False
                record.qr_pit_image = False
                record.qr_cabine = False
                record.qr_cabine_image = False
                record.qr_machine = False
                record.qr_machine_image = False

    @api.onchange('gadget_model')
    def _upper_gadget_model(self):        
        self.gadget_model = self.gadget_model.upper() if self.gadget_model else False
