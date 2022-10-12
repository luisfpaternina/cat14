from email.policy import default
from numpy import subtract
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import tzinfo, timedelta, datetime, date
from datetime import date
import datetime
from odoo.http import request
from datetime import datetime
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
        string="Team")
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
    rae_gadget = fields.Char("Product code",
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
    users_ids = fields.Many2many(
        'res.users',
        'res_users_ids',
        'user_id',
        'users_ids',
        string='Assigned to',
        store=True)
    ids_overlapping_tasks_users = fields.Char()
    overlapping_tasks_users = fields.Boolean(
        default=False)
    calculate_planed_hours = fields.Float(
        string="Subtract hours")
    progress_calculated = fields.Float(
        string="Progress percentaje",
        related="calculate_planed_hours")
    is_late_hours = fields.Boolean(
        string="Is late hours",
        compute="compute_is_late_hours")
    overlapping_tasks = fields.Boolean(default=False)
    is_end_ot = fields.Boolean(
        string="Is end OT")
    is_hr_leave_crossing = fields.Boolean(
        string="Has not leave")
    firs_assigned_id = fields.Many2one(
        'hr.employee',
        string="First assigned")
    is_full_super = fields.Boolean(
        string="Is full")
    task_cheked = fields.Boolean(
        string="Task Checked ?")


    def compute_is_late_hours(self):
        if self.effective_hours > self.planned_hours:
            self.is_late_hours = True
        else:
            self.is_late_hours = False

    @api.depends('planned_hours','effective_hours')
    def compute_subtract_hours(self):
        if self.effective_hours > 0:
            subtract = self.effective_hours - self.planned_hours
            cal = subtract * 100
            percentaje = cal - 100
            self.calculate_planed_hours =  percentaje
        else:
            self.calculate_planed_hours = 0

    @api.onchange('product_id', 'partner_id', 'name', 'ot_type_id')
    def assign_correct_technician(self):
        tecnicos = []
        tecnicos_mant = []
        responsables = []
        morning = ['08', '09', '10', '11', '12', '13', '14', '15']
        now = datetime.now()
        hours = now.strftime("%I")
        zones_obj = self.env['res.partner.zones'].search([('id', '=', self.product_id.zone_id.id)])
        if zones_obj:
            if self.ot_type_id.is_warning:
                if hours in morning:
                    for u in zones_obj:
                        tecnicos.append(u.user_notice_id.id)
                        self.users_ids = tecnicos
                else:
                    for u in zones_obj:
                        responsables.append(u.user_id.id)
                        self.users_ids = responsables
            else:
                for u in zones_obj:
                        tecnicos_mant.append(u.user_greasing_id.id)
                        self.users_ids = tecnicos_mant
        else:
            self.users_ids = False

    @api.onchange('product_id', 'partner_id', 'name')
    def gtsupervisor_id(self):
        employee_obj = self.env['hr.employee'].search([('name', '=', self.product_id.supervisor_zone_id.name)], limit=1)
        for record in self:
            if record.product_id:
                record.supervisor_id = employee_obj.id
            else:
                record.supervisor_id  = False

    def get_date_range_crossing(
        self,
        model_compare,
        planned_date_begin,
        planned_date_end
        ):
        model_crossing = []
        for rec in model_compare:
            if rec._name == 'project.task':
                r1 = rec.planned_date_begin
                r2 = rec.planned_date_end
            else:
                my_time = datetime.min.time()
                r1 = rec.request_date_from
                r1 = datetime.combine(r1, my_time)
                r2 = rec.request_date_to
                r2 = datetime.combine(r2, my_time)

            r3 = planned_date_begin
            r4 = planned_date_end

            if r3<=r1<=r4 or r3<=r2<=r4:
                model_crossing.append(rec)
            elif r1<=r3 and r4<=r2:
                model_crossing.append(rec)
            else:
                continue
        
        return model_crossing

    def get_model_user_crossing(
                                self,
                                users_ids,
                                model,
                                planned_date_begin,
                                planned_date_end):
        
        model_user_crossing = []
        for id_user in users_ids:
            if model._name == 'project.task':
                all_user_model = list(filter(lambda x: id_user in x.users_ids.ids, model))
            else:
                all_user_model = list(filter(lambda x: id_user == x.employee_id.user_id.id, model))

            tasks = self.get_date_range_crossing(
                                        all_user_model,
                                        planned_date_begin,
                                        planned_date_end
                                        )
            if tasks:
                user  = self.env['res.users'].search([('id','=', id_user)])
                data_crossing = {
                    'user': user,
                    'task': tasks
                }
                model_user_crossing.append(data_crossing)
            else:
                continue
        
        return model_user_crossing

    def get_hr_leave_crossing(self):
        fsm_task_form_view = self.env.ref('project.view_task_form2')
        fsm_task_list_view = self.env.ref('industry_fsm.project_task_view_list_fsm')
        fsm_task_kanban_view = self.env.ref('industry_fsm.project_task_view_kanban_fsm')
        ids = self.ids_overlapping_tasks_users.replace('{','')
        ids = ids.replace('}','')
        ids = ids.split(',')
        ids = list(map(int, ids))
        domain = [('id','in', ids)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Overlapping Tasks'),
            'res_model': 'project.task',
            'domain': domain,
            'views': [(fsm_task_list_view.id, 'tree'), (fsm_task_kanban_view.id, 'kanban'), (fsm_task_form_view.id, 'form')],
            'context': {
                'fsm_mode': True,
                'task_nameget_with_hours': False,
            }
        }

    @api.model
    def create(self, vals):
        if not vals['users_ids'][0][2]:
            return super(ProjectTask, self).create(vals)
        else:
            if vals['planned_date_begin'] and vals['planned_date_end']:
                users_ids = vals['users_ids']
                ids = False
                users_ids = users_ids[0][2]
                tasks_data = self.env['project.task'].search([])
                tasks_data = self.env['project.task'].search([('users_ids','!=', False),
                                                                ('planned_date_begin','!=', False),
                                                                ('planned_date_end','!=', False)])
                hr_leave_data = self.env['hr.leave'].search([])
                hr_leave_crossing = []
                tasks_user_crossing = []
                planned_date_begin = vals['planned_date_begin']
                if type(planned_date_begin) is str:
                    planned_date_begin = datetime.strptime(planned_date_begin, '%Y-%m-%d %H:%M:%S')
                
                planned_date_end = vals['planned_date_end']
                if type(planned_date_end) is str:
                    planned_date_end = datetime.strptime(planned_date_end, '%Y-%m-%d %H:%M:%S')
    
                tasks_user_crossing = self.get_model_user_crossing(
                                        users_ids,
                                        tasks_data,
                                        planned_date_begin,
                                        planned_date_end)
                if tasks_user_crossing:
                    ids = []
                    for item in tasks_user_crossing:
                        for task in item['task']:
                            ids.append(task.id)

                    ids = set(ids)

                hr_leave_crossing = self.get_model_user_crossing(
                                        users_ids,
                                        hr_leave_data,
                                        planned_date_begin,
                                        planned_date_end)

                if hr_leave_crossing:
                    users = ''
                    for item in hr_leave_crossing:
                        users += item['user'].name+" \n"
                    
                    raise ValidationError(_("Usuario: \n \n"+users+"\nla persona asignada tiene una ausencia para esa fecha"))

                res = super(ProjectTask, self).create(vals)
                for record in res:
                    if ids:
                        record.overlapping_tasks = True
                        record.ids_overlapping_tasks_users = ids
                return res
            else:
                return super(ProjectTask, self).create(vals)

    def write(self, vals):
        if not vals.get('users_ids'):
            users_ids = self.users_ids.ids
        else:
            users_ids = vals.get('users_ids')
            users_ids = users_ids[0][2]
            
        if  vals.get('planned_date_begin') or vals.get('planned_date_end'):
            if vals.get('planned_date_begin'):
                planned_date_begin = vals.get('planned_date_begin')
                planned_date_begin = datetime.strptime(planned_date_begin, '%Y-%m-%d %H:%M:%S')
            else:
                planned_date_begin = self.planned_date_begin

            if vals.get('planned_date_end'):
                planned_date_end = vals.get('planned_date_end')
                planned_date_end = datetime.strptime(planned_date_end, '%Y-%m-%d %H:%M:%S')
            else:
                planned_date_end = self.planned_date_end

            ids = False
            tasks_data = self.env['project.task'].search([])
            tasks_data = self.env['project.task'].search([('users_ids','!=', False),
                                                            ('planned_date_begin','!=', False),
                                                            ('planned_date_end','!=', False)])
            hr_leave_data = self.env['hr.leave'].search([])
            hr_leave_crossing = []
            tasks_user_crossing = []
            tasks_user_crossing = self.get_model_user_crossing(
                                    users_ids,
                                    tasks_data,
                                    planned_date_begin,
                                    planned_date_end)
            if tasks_user_crossing:
                ids = []
                for item in tasks_user_crossing:
                    for task in item['task']:
                        if task.id == self.id:
                            continue
                        ids.append(task.id)

                ids = set(ids)

            hr_leave_crossing = self.get_model_user_crossing(
                                    users_ids,
                                    hr_leave_data,
                                    planned_date_begin,
                                    planned_date_end)

            if hr_leave_crossing:
                users = ''
                for item in hr_leave_crossing:
                    users += item['user'].name+" \n"
                

                raise ValidationError(_("The users: \n \n"+users+"\nAre absent on the selected date"))
            
            if len(ids) == 0:
                vals.update({
                    'overlapping_tasks': False,
                    'ids_overlapping_tasks_users': ids,

                })
            else:
                vals.update({
                    'overlapping_tasks': True,
                    'ids_overlapping_tasks_users': ids,

                })

            return super(ProjectTask, self).write(vals)
        
        return super(ProjectTask, self).write(vals)


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

    def action_url(self):
        return {  
            'name': 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'self',
            'url'      : self.qr_scanner
            }

    #Limpiar valor campo Aparato al cambiar de Cliente, para evitar combinación incoherente.
    @api.onchange('partner_id')
    def _onchange_parner_id_clean_elevator(self):
        if self.product_id:
            self.product_id = False
    
    #Limpiar valor campo Categoría UDN al cambiar Tipo de OT, para evitar combinación incoherente.
    @api.onchange('ot_type_id')
    def _onchange_ot_type_clean_udn(self):
        if self.categ_udn_id and self.categ_udn_id.code != 'AV': #Para que no entre en conflicto con el valor por defecto de tier1.
            self.categ_udn_id = False

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
            if record.is_qr_required and record.stage_id.is_project_fsm:
                if record.check_machine == False and record.check_pit == False and record.check_cabine == False:
                    raise ValidationError(_("At least one QR code must be scanned"))
    
    def action_fsm_validate(self):
        rec = super(ProjectTask, self).action_fsm_validate()
        self.validate_check_scann_qrs()   
        return rec
    
    def change_stage_to_progress(self):
        for record in self:
            stage = self.env['project.task.type'].search([('is_progress','=', True)])
            if stage:
                record.stage_id = stage

    @api.onchange('supervisor_id')
    def get_firs_assigned_id(self):
        for record in self:
            if record.supervisor_id and record.is_full_super == False:
                record.firs_assigned_id = record.supervisor_id.id
                record.is_full_super = True
            else:
                record.supervisor_id = record.supervisor_id.id

    @api.onchange('supervisor_id')
    def send_to_supervisor(self):
        for record in self:
            if record.supervisor_id.id == record.firs_assigned_id.id:
                record.supervisor_id = record.supervisor_id
            else:
                stage = self.env['project.task.type'].search([('is_send_to_supervisor','=', True)])
                if stage:
                    record.stage_id = stage
                    
    def action_timer_start(self):
        self.change_stage_to_progress()
        return super(ProjectTask, self).action_timer_start()

    def execute_notication_task(self):
        context = self._context
        current_uid = context.get('uid')
        user_id = self.env['res.users'].browse(current_uid)
        #user_id = self.env.user
        user_id.play_alarm = True
        task = self.env['project.task'].search([('task_cheked','=',False)])
        task_user = list(filter(lambda x: user_id.id in x.users_ids.ids, task))
        if task_user:
            ids_task = [x.id for x in task_user]
            for id_task in ids_task:
                user_id._notify_channel(
                    type_message="success",
                    message="Default message",
                    title='TEST DE PRUEBA',
                    subtitle=None,
                    ref_model=task._name,
                    ref_ids=[id_task],
                    sticky=False,
                    )
        return False
    
    #Limpiar valor campo Aparato al cambiar de Cliente, para evitar combinación incoherente.
    @api.onchange('partner_id')
    def _onchange_parner_id_clean_elevator(self):
        if self.product_id:
            self.product_id = False

    #Limpiar valor campo Categoría UDN al cambiar Tipo de OT, para evitar combinación incoherente.
    @api.onchange('ot_type_id')
    def _onchange_ot_type_clean_udn(self):
        if self.categ_udn_id:
            self.categ_udn_id = False
