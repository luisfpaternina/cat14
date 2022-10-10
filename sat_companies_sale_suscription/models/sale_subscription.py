# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from pytz import timezone
import base64
import logging


class SaleSuscriptionInherit(models.Model):
    _inherit = 'sale.subscription'

    active_cron_invoice = fields.Boolean(
        string="Active cron")
    gadget_contract_type = fields.Many2one(
        'stock.gadgets.contract.type',
        string="Contract type")
    is_potential_client = fields.Boolean(
        string="Is a potential client",
        tracking=True,
        related="partner_id.is_potential_client")
    product_id = fields.Many2one(
        'product.template',
        'Gadgets')
    task_user_id = fields.Many2one(
        'res.users')
    sale_type_id = fields.Many2one(
        'sale.order.type')
    gadgest_contract_type_id = fields.Many2one(
        'stock.gadgets.contract.type')
    date_begin = fields.Datetime(
        string = 'Date asigned')
    date_end = fields.Datetime(
        string = 'Date End asingned')
    check_contract_type = fields.Boolean(
        compute="_compute_check_contract_type",
        )
    signature = fields.Image(
        'Signature',
        help='Signature received through the portal.',
        copy=False,
        attachment=True,
        max_width=1024,
        max_height=1024)
    signed_by = fields.Char(
        'Signed By',
        help='Name of the person that signed the SO.',
        copy=False)
    signed_on = fields.Datetime(
        'Signed On',
        help='Date of the signature.',
        copy=False)
    pdf_file_sale_contract = fields.Binary(
        'PDF Contrato',
        attachment=True)
    is_extension = fields.Boolean(
        string="Is extension",
        tracking=True)
    is_extension_stage = fields.Boolean(
        string="Is extension stage",
        compute="_compute_extension_stage")
    recurring_rule_boundary = fields.Selection(
        string="Duration",
        related="template_id.recurring_rule_boundary")
    document_ids = fields.Many2many(
        'ir.attachment',
        string="SUBA SU ARCHIVO",
        help='Please attach Documents',
        copy=False,
        tracking=True)
    low_date = fields.Date(
        string="Low date")
    res_partner_low_mto_id = fields.Many2one(
        'res.partner',
        string="Low mto")
    is_suspension_stage = fields.Boolean(
        string="Is suspension stage")
    check_signature = fields.Boolean(
        string="Check signature")
    pdf_file_welcome = fields.Binary(
        string="PDF file welcome",
        compute="action_get_attachment")
    signature_url_text = fields.Text(
        string="Signature URL")
    stage_code = fields.Char(
        string="Code",
        related="stage_id.stage_code")
    show_technical = fields.Boolean(
        string="Enable technical",
        compute="compute_show_technical")
    exclude_months = fields.Boolean(
        'Exlude Months')
    subscription_month_ids = fields.Many2many(
        'sale.subscription.month')
    udn_type_id = fields.Many2one(
        'project.task.categ.udn',
        string="Udn")
    lines_count = fields.Integer(
        string="Lines count",
        compute="compute_lines_count")
    is_progress = fields.Boolean(
        string="Is progress",
        related="stage_id.is_progress")


    @api.depends('recurring_invoice_line_ids')
    def compute_lines_count(self):
        for record in self:
            if record.recurring_invoice_line_ids:
                for line in record.recurring_invoice_line_ids:
                    count = len(record.recurring_invoice_line_ids)
                    record.lines_count = count
            else:
                record.lines_count = 0

    @api.depends('partner_id', 'product_id')
    def compute_show_technical(self):
        show_technical = self.env['ir.config_parameter'].sudo().get_param('sat_companies.show_technical') or False
        self.show_technical = show_technical

    def action_welcome_email_send(self):
        self.contract_send = True
        self.ensure_one()
        template = self.env.ref('sat_companies_sale_suscription.template_email_welcome')
        lang = self.env.context.get('lang')
        template_id = template.id
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.subscription',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    
    def _compute_file_welcome_email(self):
        pdf = self.env.ref('sat_companies_sale_suscription.template_email_welcome').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

    @api.depends('check_signature')
    def action_get_attachment(self):
        for record in self:
            if record.check_signature == True:
                pdf = self.env.ref('sat_companies_sale_suscription.template_email_welcome')._render_qweb_pdf(self.ids)
                print(pdf)
                b64_pdf = base64.b64encode(pdf[0])
                record.pdf_file_welcome = b64_pdf
                if record.order_line:
                    for line in record.order_line:
                        line.subscription_id.pdf_file_sale_contract = record.pdf_file_welcome
            else:
                record.pdf_file_welcome = False
    
    def button_rejected_stage(self):
        rs = self.env['sale.subscription.stage'].search([('stage_code', '=', '1')], limit=1)
        self.write({'stage_id': rs.id})

    @api.onchange('product_id')
    def onchange_product_gadget_id(self):
        if self.product_id:
            self.low_date = self.product_id.low_date
            self.res_partner_low_mto_id = self.product_id.res_partner_low_mto_id.id

    @api.depends('stage_id')
    def _compute_extension_stage(self):
        for record in self:
            if record.stage_id.stage_code == '2':
                record.is_extension_stage = True
            else:
                record.is_extension_stage = False
    
    @api.onchange('stage_id')
    def _compute_suspension_stage(self):
        for record in self:
            if record.stage_id.stage_code == '01':
                record.is_suspension_stage = True
            else:
                record.is_suspension_stage = False

    @api.onchange('product_id')
    def _template_gadget(self):
        for record in self:
            record.template_id = record.product_id.subscription_template_id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleSuscriptionInherit, self).onchange_partner_id()
        for record in self:
            if record.partner_id.payment_term_maintenance_id:
                record.payment_term_id = record.partner_id.payment_term_maintenance_id
        return res

    def start_subscription(self):
        res = super(SaleSuscriptionInherit, self).start_subscription()
        for record in self:
            project_fsm = self.env.ref('industry_fsm.fsm_project', raise_if_not_found=False)

            new_task = self.env['project.task'].sudo().create({
                'name': record.name,
                'partner_id': record.partner_id.id,
                'ot_type_id': record.sale_type_id.id,
                'gadgest_contract_type_id': record.gadgest_contract_type_id.id,
                'project_id': project_fsm.id,
                'user_id': record.task_user_id.id,
                'product_id': record.product_id.id,
                'planned_date_begin': record.date_begin, 
                'planned_date_end': record.date_end,
                'is_fsm': True

            })
        return res

    @api.onchange('product_id')
    def onchange_check_product(self):
        for record in self:
            if record.product_id.employee_notice_id.user_id:
                record.task_user_id = record.product_id.employee_notice_id.user_id
            sale_type = record.product_id.subscription_template_id.sale_type_id
            gadgets_contract = record.product_id.subscription_template_id.gadgets_contract_type_id
            record.sale_type_id = sale_type
            record.gadgest_contract_type_id = gadgets_contract

    @api.depends('sale_type_id')
    def _compute_check_contract_type(self):
        for record in self:
            record.type_contract = False
            if record.sale_type_id.code == '01':
                record.check_contract_type = True
            else:
                record.check_contract_type = False

    @api.constrains('partner_id')
    def _validate_is_potential_client(self):
        for record in self:
            if record.is_potential_client:
                raise ValidationError(_(
                    'Validate potential client in partner'))

    @api.onchange('team_id')
    def _onchange_team(self):
        for record in self:
            print('team')

    @api.onchange('sale_type_id', 'product_id')
    def domain_udn_type(self):
        for record in self:
            if record.sale_type_id:
                return {'domain': {'udn_type_id': [('ot_type_id', '=', record.sale_type_id.id)]}}
            else:
                return {'domain': {'udn_type_id': []}}

    def _recurring_create_invoice(self):
        res = super(SaleSuscriptionInherit, self)._recurring_create_invoice()
        for record in self:
            recurring_interval = record.template_id.recurring_interval
            #active_cron = record._active_cron_invoice(active_cron)
            if record.exclude_months == True:
                #if active_cron == True:
                #    date_today = datetime.now().month
                #else:
                date_today = datetime.now().month
                period = 1
                months_number = []
                period_number = []
                months = range(12)
                c = 1
                for m in months:
                    months_number.append(m+1)
                    if c > recurring_interval:
                        period += 1
                        c=1
                    period_number.append(period)

                    c += 1

                tuple_months = dict(zip(months_number, period_number))

                for t in tuple_months:
                    if date_today == t:
                        p = tuple_months[t]
                        m = 0
                        tuple_m = []
                        for t_1 in tuple_months:
                            if p == tuple_months[t_1]:
                                tuple_m.append([t_1,tuple_months[t_1]])


                        if tuple_m:
                            m = []
                            for t in tuple_m:
                                for monthn_check in record.subscription_month_ids:
                                    if t[0] == monthn_check.code:
                                        m.append(t)

                if res.invoice_line_ids:
                        for line in res.invoice_line_ids:
                            total = line.price_unit
                        
                        free_month_product =self.env.ref(
                        'sat_companies_sale_suscription.free_month_product_service'
                        )
                        line_last_product = res.invoice_line_ids[-1]
                        vals_lines = []
                        for t in m:
                            month_name = self.env['sale.subscription.month'].search([('code','=',str(t[0]))],limit=1)
                            vals_line = (0,0,{
                                    'name': 'Descuento total por mes'+' '+month_name.name,
                                    'product_id': free_month_product.id,
                                    'tax_ids': line_last_product.tax_ids.ids,
                                    'price_unit': -total,
                                    'quantity': 1,
                                })
                            vals_lines.append(vals_line)
                            
                        vals = {
                                'product_id': record.product_id.id,
                                'task_user_id': record.task_user_id.id,
                                'sale_type_id': record.sale_type_id.id,
                                'gadgets_contract_type_id': record.gadgest_contract_type_id.id,
                                'invoice_line_ids': vals_lines,
                                }
                        res.write(vals)
            
            else:
                if record.product_id:
                    vals = {
                                'product_id': record.product_id.id,
                                'task_user_id': record.task_user_id.id,
                                'sale_type_id': record.sale_type_id.id,
                                'gadgets_contract_type_id': record.gadgest_contract_type_id.id
                                }
                    res.write(vals)

        return res
