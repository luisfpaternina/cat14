from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import datetime

class ProjectTask(models.Model):
    _inherit = 'project.task'

    minute_point_ids = fields.Many2many(
        'maintenance.minute.point',
        string="Minute point")
    checklist_line_ids = fields.One2many(
        'project.task.checklist.minute',
        'task_id',
        string="checklist lines")
    checklist_ids = fields.Many2many(
        'project.task.ot.checklist',
        string="Checklist",
        tracking=True)
    inspection_id = fields.Many2one(
        'project.task.inspection',
        string="Inspection",
        tracking=True)
    gadget_id = fields.Many2one(
        'stock.gadgets',
        string="Gadget")
    product_id = fields.Many2one(
        'product.template',
        string="Gadget")
    gadget_code = fields.Char(
        string="Gadget code",
        related="product_id.code")
    population_name = fields.Char(
        string="Population name",
        related="product_id.population_id.name")
    population_code = fields.Char(
        string="Population code",
        related="product_id.population_id.code")
    address = fields.Char(
        string="Address",
        related="product_id.address")
    address2 = fields.Char(
        string="Address 2",
        related="product_id.address2")
    address3 = fields.Char(
        string="Address 3",
        related="product_id.address3")
    reference = fields.Char(
        string="Reference",
        related="product_id.default_code")
    contact_person = fields.Char(
        string="Pers.Ctto")
    phone_contact = fields.Char(
        string="Phone")
    fax_contact = fields.Char(
        string="FAX")
    email_contact = fields.Char(
        string="Email")
    delegation_id = fields.Many2one(
        'res.partner.delegation',
        string="Delegation",
        related="product_id.delegation_id")
    delegation_name = fields.Char(
        string="Delegation name",
        related="delegation_id.name")
    ot_date = fields.Datetime(
        string="Date",
        default=date.today())
    month_date = fields.Char(
        string="Month",
        compute="calculate_month")
    ot_ref = fields.Char(
        string="Ref. Obra OT")
    received_material = fields.Char(
        string="Received material")
    is_pending_validate = fields.Boolean(
        string="Pending to validate")
    situation = fields.Selection([
        ('pending','Pending'),
        ('started','Started'),
        ('finished','Finished')],string="Situation")
    is_pda = fields.Boolean(
        string="PDA",
        related="supervisor_id.pda")
    ot_description = fields.Text(
        string="Observations")
    supervisor_id = fields.Many2one(
        'hr.employee',
        string="Supervisor",
        related="product_id.employee_notice_id")
    prev_start_date = fields.Datetime(
        string="Prev start date")
    actual_start_date = fields.Datetime(
        string="Actual start date")
    prev_end_date = fields.Datetime(
        string="Prev end date")
    actual_end_date = fields.Datetime(
        string="Actual end date")
    verification_date = fields.Datetime(
        string="Verification date")
    associated_type_id = fields.Many2one(
        'project.task.type.associated',
        string="Associated type")
    task_signature = fields.Binary(
        string="Client signature")
    checklist_ot_ids = fields.One2many(
        'project.task.ot.checklist.line',
        'task_id',
        string="Ot checklist")
    categ_udn_id = fields.Many2one(
        'project.task.categ.udn',
        string="Category/Udn OT")
    zone_id = fields.Many2one(
        'res.partner.zones',
        string="Zone",
        related="product_id.zone_id")
    zone_name = fields.Char(
        string="Zone name",
        related="zone_id.name")
    rae = fields.Char(
        string="R.A.E",
        related="product_id.rae")
    ot_type_id = fields.Many2one(
        'sale.order.type',
        string="OT type")
    is_maintenance = fields.Boolean(
        string="Is maintenance")
    name_of_signatory = fields.Char(
        string="Name of signatory")
    dni = fields.Char(
        string="DNI")
    floor = fields.Char(
        string="Floor")
    ot_code = fields.Char(
        string="OT code")
    notes = fields.Text(
        string="Notes")
    breakdowns_id = fields.Many2one(
        'project.task.breakdowns',
        string="Breakdowns")
    is_warning = fields.Boolean(
        string="Is warning")
    stop_type = fields.Selection([
        ('yes','Yes'),
        ('not','Not')],string="Stop")
    is_apartament = fields.Boolean(
        string="Is apartament")
    is_blocked = fields.Boolean(
        string="is Blocked")
    service_h = fields.Boolean(
        string="Service 24h")
    breakdowns_notice = fields.Text(
        string="Breakdowns notice")
    is_conflictive_apparatus = fields.Boolean(
        string="Is conflictive apparatus")
    done_work = fields.Text(
        string="Done work")
    contact_person_ot = fields.Char(
        string="Contact Person OT")
    contact_person_telephone = fields.Char(
        string="Telephone contact")
    is_stop_with_company = fields.Boolean(
        string="Is stop with company")
    gadget_pda_observations = fields.Text(
        string="Gadget PDA observations")
    gadget_notes = fields.Text(
        string="Gadget notes")
    floor_number = fields.Char(
        string="Floor number")
    maximum_rescue_time = fields.Float(
        string="Maximum rescue time")
    maximum_warning_time = fields.Float(
        string="Maximum warning time")
    is_technical_notice_ot = fields.Boolean(
        string="Is technical notice")
    community_mood_id = fields.Many2one(
        'task.community.mood',
        string="Community mood")
    reading_date = fields.Datetime(
        string="Reading date")
    assignment_date = fields.Datetime(
        string="Assignment date")



    @api.onchange('ot_type_id')
    def domain_udn(self):
        for record in self:
            if record.ot_type_id:
                return {'domain': {'categ_udn_id': [('ot_type_id', '=', record.ot_type_id.id)]}}
            else:
                return {'domain': {'categ_udn_id': []}}

    @api.onchange('contact_person')
    def _capitalizate_name(self):        
        self.contact_person = self.contact_person.title() if self.contact_person else False

    @api.depends('ot_date')
    def calculate_month(self):
        for record in self:
            dt = datetime.datetime.today()
            record.month_date = dt.month

    @api.onchange('checklist_ot_ids')
    def _onchange_checklist(self):
        self.checklist_ot_ids.onchange_checklist()

    @api.constrains('checklist_ot_ids')
    def _check_exist_record_in_lines(self):
        for rec in self:
            exis_record_lines = []
            for line in rec.checklist_ot_ids:
                if line.checklist_id.id in exis_record_lines:
                    raise ValidationError(_('The column should be one per line'))
                exis_record_lines.append(line.checklist_id.id)
