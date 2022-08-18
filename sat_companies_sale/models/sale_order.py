# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import base64
import logging

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    address = fields.Char(
        string="Address",
        related="partner_id.street",
        tracking=True)
    population_id = fields.Many2one(
        'res.partner.population',
        string="Population",
        tracking=True)
    sale_type = fields.Selection([
        ('maintenance','Maintenance'),
        ('mounting','Mounting'),
        ('repair','Repair')],string="Sale type")
    type_contract = fields.Selection([
        ('normal','Normal'),
        ('risk','All risk')],string="Contract type")
    is_create_task = fields.Boolean(
        string="Create task",
        tracking=True,
        related="sale_type_id.is_create_task")
    check_contract_type = fields.Boolean(
        compute="_compute_check_contract_type",
        )
    type_service_id = fields.Many2many(
        'sale.type.service',
        string='Type service'
        )
    pdf_file_sale_contract = fields.Binary(
        compute="action_get_attachment")
    signature_url_text = fields.Text(
        string="Signature URL")
    check_signature = fields.Boolean(
        string="Check signature")
    is_forecast_made = fields.Boolean(  
        string="Forecast Made")
    product_id = fields.Many2one(
        'product.template',
        string='Gadget')
    task_user_id = fields.Many2one(
        'res.users',
        'Task User id')
    check_product = fields.Boolean(
        compute='compute_check_product')
    date_begin = fields.Datetime(
        string="Date begin")
    date_end = fields.Datetime(
        string="Date end")
    quote_date_sent = fields.Date(
        string="Quote date sent",
        compute="_calculated_quote_date_sent")
    quote_date_sent_min = fields.Date(
        string="Quote date sent min")
    rae = fields.Char(
        string="R.A.E",
        related="product_id.rae")
    contract_send = fields.Boolean()
    pdf_description = fields.Char(
        string="PDF description",
        tracking=True)
    is_pdf_true = fields.Boolean(
        string="PDF True")
    udn_id = fields.Many2one(
        'project.task.categ.udn',
        string="Udn")
    is_maintenance = fields.Boolean(
        string="Is maintenance")
    is_line = fields.Boolean(
        string="Is line")
    is_other = fields.Boolean(
        string="Other")
    is_mounting = fields.Boolean(
        string="Is mounting")
    is_normative = fields.Boolean(
        string="Normative",
        related="udn_id.is_normative")
    normative_date = fields.Date(
        string="Normative date")
    show_technical = fields.Boolean(
        string="Enable technical",
        compute="compute_show_technical")
    sign_contract_date = fields.Date(
        string="Sign contract date",
        compute="compute_contract_date")
    user_partner_contact_id = fields.Many2one(
        'res.users',
        string="Comercial mantenimiento",
        tracking=True)
    is_conditioned = fields.Boolean(
        string="Is conditioned")

    @api.onchange('partner_id')
    def maintenance_partner(self):
        for record in self:
            if record.partner_id:
                record.user_partner_contact_id = record.partner_id.user_partner_contact_id.id

    @api.depends('state','pdf_file_sale_contract')
    def compute_contract_date(self):
        now = datetime.now()
        for rec in self:
            if rec.pdf_file_sale_contract:
                rec.sign_contract_date = now
            else:
                rec.sign_contract_date = False

    @api.depends('partner_id', 'product_id')
    def compute_show_technical(self):
        show_technical = self.env['ir.config_parameter'].sudo().get_param('sat_companies.show_technical') or False
        self.show_technical = show_technical

    @api.onchange('sale_type_id', 'product_id')
    def domain_udns(self):
        for record in self:
            if record.sale_type_id:
                return {'domain': {'udn_id': [('ot_type_id', '=', record.sale_type_id.id)]}}
            else:
                return {'domain': {'udn_id': []}}

    @api.onchange('sale_type_id')
    def domain_saletemplate(self):
        for record in self:
            if record.sale_type_id:
                return {'domain': {'sale_order_template_id': [('sale_type_id', '=', record.sale_type_id.id)]}}
            else:
                return {'domain': {'sale_order_template_id': []}}

    @api.onchange('state','name')
    def send_pdf_description(self):
        for record in self:
            if record.pdf_file_sale_contract:
                record.pdf_description = 'CONTRATO HA SIDO FIRMADO'

    @api.onchange('product_id')
    def onchange_check_product(self):
        for record in self:
            if record.product_id.employee_notice_id.user_id:
                record.task_user_id = record.product_id.employee_notice_id.user_id
            sale_type = record.product_id.subscription_template_id.sale_type_id
            gadgets_contract = record.product_id.subscription_template_id.gadgets_contract_type_id
            if sale_type:
                record.sale_type_id = sale_type
            if gadgets_contract:
                record.gadgets_contract_type_id = gadgets_contract

    @api.depends('product_id')
    def compute_check_product(self):
        for record in self:
            if record.product_id:
                record.check_product=True
            else:
                record.check_product=False
        
    @api.depends('sale_type_id')
    def _compute_check_contract_type(self):
        for record in self:
            record.type_contract = False
            if record.sale_type_id.code == '01':
                record.check_contract_type = True
            else:
                record.check_contract_type = False

    @api.onchange('type_service_id')
    def get_item_count(self):
        for rec in self:
            count = 1
            for line in rec.type_service_id:
                line.item = count
                count += 1

    def get_table_type_contracts(self):
        flag = False
        table = '<ul>'
        for  type_service_id in self.type_service_id:
            flag = True
            table += '<li>' + str(type_service_id.type_service_id.name) + '  </li>'
        
        table += '</ul>'
        return table if flag else False

    def action_contract_send(self):
        self.contract_send = True
        self.ensure_one()
        template = self.env.ref('sat_companies_sale.email_contract_signature')
        lang = self.env.context.get('lang')
        template_id = template.id
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
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

    def _compute_file_sale_contract(self):
        pdf = self.env.ref('sat_companies_sale.action_email_contract_signature').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

    @api.depends('check_signature')
    def action_get_attachment(self):
        for record in self:
            if record.check_signature == True:
                pdf = self.env.ref('sat_companies_sale.action_email_contract_signature')._render_qweb_pdf(self.ids)
                print(pdf)
                b64_pdf = base64.b64encode(pdf[0])
                record.pdf_file_sale_contract = b64_pdf
                if record.order_line:
                    for line in record.order_line:
                        line.subscription_id.pdf_file_sale_contract = record.pdf_file_sale_contract 
            else:
                record.pdf_file_sale_contract = False

    @api.depends('partner_id', 'state')
    def _calculated_quote_date_sent(self):
        today = date.today()
        for record in self:
            if record.state == 'sent':
                record.quote_date_sent = today
            elif record.state == 'done':
                record.quote_date_sent = today
            else:
                record.quote_date_sent = False

    def action_send_email_welcome(self):
    # FUNCIÓN PARA ENVIAR CORREOS CON PDF ADJUNTO
        self.ensure_one()
        wizard = self.env['sale.order']
        wizard = wizard.create({
                'name': self.name,
                'partner_id': self.partner_id.id,
        })
        # Se agrega PDF
        pdf = self.env.ref('sat_companies_sale.id_welcome_mjs')._render_qweb_pdf(wizard.id)
        b64_pdf = base64.b64encode(pdf[0])
        ATTACHMENT_NAME = 'Carta de bienvenida' + '-' + self.name
        attach_report = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })
        # Se agrega plantilla de correo
        template_id = self.env['ir.model.data'].xmlid_to_res_id('sat_companies_sale.template_email_welcome_sale', raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        template.attachment_ids = [(6,0,[attach_report.id])]
        if template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.ids)
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
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
