# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .qr_code_base import generate_qr_code
import base64
from io import BytesIO
import qrcode

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
        tracking=True,
        readonly=True,
        required=True,
        copy=False,
        default='New')
    partner_id = fields.Many2one(
        'res.partner',
        string="Client",
        tracking=True)
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
        tracking=True,
        related="partner_id.street")
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
        tracking=True)
    length = fields.Float(
        string="Length",
        tracking=True)
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
        string="Delegation")
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
    bench = fields.Selection([
        ('high','High'),
        ('low','Low')],string="Bench")
    motor_power = fields.Char(
        string="Motor power")
    motor_brake = fields.Char(
        string="Motor brake")
    number_stops = fields.Integer(
        string="Number of stops")
    numer_people = fields.Integer(
        string="Number of people")
    load = fields.Float(
        string="Load")
    nominal_speed = fields.Float(
        string="Nominal speed")
    route = fields.Char(
        string="Gadget route")
    is_reduced_pit = fields.Boolean(
        string="Reduced pit")
    is_reduced_flight = fields.Boolean(
        string="Reduced flight")
    gate_operator = fields.Char(
        string="Gate operator")
    shipment = fields.Selection([
        ('simple','Simple'),
        ('double','Doble'),
        ('triple','Triple')],string="Shipment")
    soil_type_id = fields.Many2one(
        'stock.soil.type',
        string="Soil type")
    cockpit_keypad_id = fields.Many2one(
        'stock.cockpit.type',
        string="Cockpit keypad type")
    cockpit_push_id = fields.Many2one(
        'stock.cockpit.push.type',
        string="Cockpit push type")
    wash_cabin = fields.Char(
        string="Wash cabin")
    traction_cables = fields.Float(
        string="Traction cables")
    maneuver = fields.Char(
        string="Maneuver")
    maneuvering_box = fields.Char(
        string="Maneuvering box")
    belt_operator = fields.Char(
        string="Belt operator")
    is_operator_brake = fields.Boolean(
        string="Operator brake")
    is_timed_cabin_light = fields.Boolean(
        string="Timed cabin light")
    cabin_tube_types = fields.Char(
        string="Cabin tube types")
    number_of_tubes = fields.Integer(
        string="N° tubes")
    is_weighing_scales = fields.Boolean(
        string="Weighing scales")
    tractor_pulley = fields.Float(
        string="Tractor pulley")
    tensioner_pulley = fields.Float(
        string="Tensioner pulley")
    limiter_pulley = fields.Float(
        string="Limiter pulley")
    deflection_pulley = fields.Float(
        string="Deflection pulley")
    counterweight_pulley = fields.Float(
        string="Counterweight pulley")
    counterweight_wedging = fields.Boolean(
        string="Counterweight wedging")
    cabine_wedging = fields.Boolean(
        string="Cabine wedging")
    cabin_puffer = fields.Boolean(
        string="Cabin puffer")
    counterweight_puffer = fields.Boolean(
        string="Counterweight puffer")
    bidirectional_model = fields.Char(
        string="Bidirectional model")
    gsm_model = fields.Char(
        string="Model GSM")
    line = fields.Selection([
        ('1','fixed'),
        ('2','movil')],string="Line")
    is_netel_line = fields.Boolean(
        string="Netel line")
    landing_gate = fields.Selection([
        ('1','Manual'),
        ('2','Automatic'),
        ('3','Semiautomatic')],string="Landing gate")
    landing_keypad = fields.Char(
        string="Landing keypad")
    landing_lock = fields.Char(
        string="Landing lock")
    landing_key = fields.Char(
        string="Landing key")
    company_id = fields.Many2one(
    'res.company',
    'Company',
    default=lambda self: self.env.user.company_id 
    )
    company_product_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id)
    
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


    # Ejecutar Secuencia 
    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('gadgets') or 'New'
        result = super(ProductTemplate, self).create(vals)
        return result


    @api.constrains('start_date_contract','end_date_contract')
    def validate_contracs_dates(self):
        if self.start_date_contract > self.end_date_contract:
            raise ValidationError(_(
                'The contract start date cannot be greater than the end date'))


    @api.onchange('gadget_model')
    def _upper_gadget_model(self):        
        self.gadget_model = self.gadget_model.upper() if self.gadget_model else False


    @api.constrains('number_stops')
    def _check_number_stops(self):
        for record in self:
            if record.number_stops < 0:
                raise ValidationError(_(
                    "The number of stops cannot lesser cero! : %s" % record.number_stops))


    @api.constrains('numer_people')
    def _check_number_people(self):
        for record in self:
            if record.numer_people < 0:
                raise ValidationError(_(
                    "The number of people cannot lesser cero! : %s" % record.numer_people))
