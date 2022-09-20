from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import datetime
import logging

class ProjectTask(models.Model):
    _inherit = 'project.task'

    minute_point_ids = fields.Many2many(
        'maintenance.minute.point',
        string="Minute point")
    checklist_line_ids = fields.One2many(
        'project.task.ot.checklist.line',
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
        related="product_id.ref")
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
        string="Delegation")
    delegation_name = fields.Char(
        string="Delegation name",
        related="delegation_id.name")
    ot_date = fields.Date(
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
        string="PDA")
    ot_description = fields.Text(
        string="Observations")
    supervisor_id = fields.Many2one(
        'hr.employee',
        string="Supervisor")
    prev_start_date = fields.Date(
        string="Prev start date")
    actual_start_date = fields.Date(
        string="Actual start date")
    prev_end_date = fields.Date(
        string="Prev end date")
    actual_end_date = fields.Date(
        string="Actual end date")
    verification_date = fields.Date(
        string="Verification date")
    ot_type_id = fields.Many2one(
        'sale.order.type',
        string="Type")
    associated_type_id = fields.Many2one(
        'project.task.type.associated',
        string="Associated type")
    task_signature = fields.Binary(
        string="Signature")
    checklist_ot_ids = fields.One2many(
        'project.task.ot.checklist.line',
        'task_id',
        string="Ot checklist")


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
