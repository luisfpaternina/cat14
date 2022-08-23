from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import tzinfo, timedelta, datetime
from odoo.http import request
import base64
from io import BytesIO
import qrcode

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    ##QR SCANNER FIELDS##
    qr_scanner = fields.Char(
        'Qr Scanner')
    state_check_qr = fields.Selection([
        ('checking','Checking'),
        ('done','Done')],string="State Check Gagdest", default='checking', tracking=True)
    delegation = fields.Many2one(
        'res.partner.delegation',
        string="Delegation")
    from_gadget = fields.Many2one(
        'stock.gadgets',
        string="From the Gadget")
    to_gadget = fields.Many2one(
        'stock.gadgets',
        string="To the Gadget")
    from_zone = fields.Many2one(
        'res.partner.zones',
        string="From the Zone")
    to_zone = fields.Many2one(
        'res.partner.zones',
        string="To the Zone")
    delegation_location = fields.Char(
        string="Name",
        related='delegation.name')
    from_gadget_location = fields.Char(
        string="Name",
        related='from_gadget.name')
    to_gadget_location = fields.Char(
        string="Name",
        related='to_gadget.name')
    from_zone_location = fields.Char(
        string="Name",
        related='from_zone.name')
    to_zone_location = fields.Char(
        string="Name",
        related='to_zone.name')
    qr_scanner = fields.Char(
        string = 'Qr Scanner')
    check_pit = fields.Boolean(
        string = 'Pit', tracking=True)
    check_cabine = fields.Boolean(
        string = 'Cabine', tracking=True)
    check_machine = fields.Boolean(
        string = 'Machine', tracking=True)
    qr_pit = fields.Binary(
        'Dowload Qr Image Pit',
        related="product_id.qr_pit")
    qr_pit_image = fields.Binary(
        'QR CODE IMAGE PIT',
        related="product_id.qr_pit_image")
    qr_cabine = fields.Binary(
        'Dowload QR Image Cabine',
        related="product_id.qr_cabine")
    qr_cabine_image = fields.Binary(
        'QR CODE IMAGE CABINE',
        related="product_id.qr_cabine_image")
    qr_machine = fields.Binary(
        'Dowload QR Image Machine',
        related="product_id.qr_machine")
    qr_machine_image = fields.Binary(
        'QR CODE IMAGE MACHINE',
        related="product_id.qr_machine_image")
    check_qr_active = fields.Boolean(
        'Check Qr')
    pit_confirm = fields.Boolean(
        'Pit confirm')
    cabin_confirm = fields.Boolean(
        'Cabine confirm')
    machine_confirm = fields.Boolean(
        'Machine confirm')
    rae_gadget = fields.Char("R.A.E",
                            related="product_id.rae")
    check_suscription_recurrent = fields.Boolean(
        "Suscription recurrent",
        compute="compute_check_suscription_recurrent")
    check_pit_datetime = fields.Datetime(
        'Check Datetime Pit')
    check_cabine_datetime = fields.Datetime(
        'Check Datetime Cabine')
    check_machine_datetime = fields.Datetime(
        'Check Datetime Machine')
    order_lines = fields.One2many(
        'sale.order.line',
        'task_id')
    ot_type_id = fields.Many2one(
        'sale.order.type',
        string="Tipo OT")
    gadgest_contract_type_id = fields.Many2one(
        'stock.gadgets.contract.type',
        string="Tipo Suscripción")
    payment_term_ot_id = fields.Many2one(
        'account.payment.term',
        string="Payment term")
    picking_ids = fields.Many2many(
        'stock.picking',
        'stock_picking_rel',
        string="Picking")
    is_maintenance = fields.Boolean(
        string="Is maintenance",
        related="ot_type_id.is_maintenance")
    is_old_task = fields.Boolean(
        string="Is old task",
        default=True)
    task_code = fields.Char(
        string="Task code")
    comercial_description = fields.Html(
        string="Description")
    origin = fields.Char(
        string="Origin")
    is_warning = fields.Boolean(
        string="Is warning",
        related="ot_type_id.is_warning")
    is_qr_required = fields.Boolean(
        string="Is QR required?")

    allowed_user_ids = fields.Many2many('res.users')

    @api.onchange('partner_id','ot_type_id')
    def _payment_terms(self):
        for record in self:
            if record.ot_type_id.is_maintenance:
                record.payment_term_ot_id = record.partner_id.payment_term_maintenance_id
            elif record.ot_type_id.is_line:
                record.payment_term_ot_id = record.partner_id.payment_term_tel_id
            else:
                record.payment_term_ot_id = record.partner_id.property_payment_term_id

    @api.onchange('categ_udn_id')
    def related_type_ot(self):
        for record in self:
            record.ot_type_id = record.categ_udn_id.ot_type_id

    def compute_check_suscription_recurrent(self):
        for record in self:
            suscription_template_log = self.env['sale.subscription.log'].search([('project_task_id','=',record.id)])
            if suscription_template_log:
                suscription_template = suscription_template_log.subscription_id
                if suscription_template.stage_id.sequence == 20:
                    record.check_suscription_recurrent = True
                else:
                    record.check_suscription_recurrent = False
            else:
                record.check_suscription_recurrent = False

    def confirm_check_gadget(self):
        for record in self:
            if record.qr_scanner:
                if 'pit' in record.qr_scanner or 'machine' in record.qr_scanner or 'cabine' in record.qr_scanner:
                    scanner_value = record.qr_scanner.split(",")
                    gadget_value = scanner_value[0]
                    id_product = int(scanner_value[1])
                    domain = ('product_id','=',id_product)
                    project_task = self.env['project.task'].search([domain])
                    for task in project_task:
                        if gadget_value == 'pit':
                            task.check_pit = True
                            task.check_pit_datetime = datetime.now()
                            record.pit_confirm = True
                            record.cabin_confirm = False
                            record.machine_confirm = False
                            record.qr_scanner = False
                        elif gadget_value == 'machine':
                            task.check_machine = True
                            task.check_machine_datetime = datetime.now()
                            record.pit_confirm = False
                            record.cabin_confirm = False
                            record.machine_confirm = True
                            record.qr_scanner = False
                        elif gadget_value == 'cabine':
                            task.check_cabine = True
                            task.check_cabine_datetime = datetime.now()
                            record.pit_confirm = False
                            record.cabin_confirm = True
                            record.machine_confirm = False
                            record.qr_scanner = False
    
    @api.onchange('qr_scanner')
    def _onchange_qr_scanner(self):
        for record in self:
            if record.qr_scanner:
                record.check_qr_active = True
            else:
                record.check_qr_active = False

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        for record in self:
            if 'check_pit' in vals or 'check_cabine' in vals or 'check_machine' in vals :
                if record.check_pit == True and record.check_cabine == True and record.check_machine == True:
                    record.state_check_qr = 'done'
                else:
                    record.state_check_qr = 'checking'

    def action_url(self):
        return {  
            'name': 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'self',
            'url'      : self.qr_scanner
            }

    @api.constrains(
        'check_machine',
        'check_cabine',
        'check_pit',
        'name',
        'partner_id'
        'stage_id')
    def validate_check_scann_qrs(self):
    # VALIDAR QUE AL MENOS UN QR SEA ESCANEADO ANTES DE MARCAR COMO HECHO
        qr_required = self.env['ir.config_parameter'].sudo().get_param('sat_companies.is_qr_required') or False
        for record in self:
            record.is_qr_required = qr_required
            if record.is_qr_required and record.stage_id.sequence == 5:
                if record.check_machine == False and record.check_pit == False and record.check_cabine == False:
                    raise ValidationError(_("At least one QR code must be scanned"))
    
    def action_fsm_validate(self):
        rec = super(ProjectTask, self).action_fsm_validate()
        self.validate_check_scann_qrs()   
        return rec
