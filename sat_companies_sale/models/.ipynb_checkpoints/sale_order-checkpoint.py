# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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

    type_service_id = fields.One2many(
        'sale.check.type.contract',
        'order_id',
        string='Type service'
        )
    pdf_file_sale_contract = fields.Binary(compute="action_get_attachment")
    signature_url_text = fields.Text()
    check_signature = fields.Boolean()

    @api.depends('sale_type_id')
    def _compute_check_contract_type(self):
        for record in self:
            record.type_contract = False
            if record.sale_type_id.code == '01':
                record.check_contract_type = True
            else:
                record.check_contract_type = False


    @api.constrains('contract_line_ids')
    def _check_exist_record_in_lines(self):
        for rec in self:
            exis_record_lines = []
            for line in rec.contract_line_ids:
                if line.contact_id.id in exis_record_lines:
                    raise ValidationError(_(
                        'The item should be one per line'))
                exis_record_lines.append(line.contact_id.id)

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
        """
        for record in self:
            pdf_file = self.env.ref('sat_companies_sale.action_email_contract_signature').report_action(self)
            if pdf_file:
                record.pdf_file_sale_contract = pdf_file
            else:
                record.pdf_file_sale_contract = False
        """
    @api.depends('check_signature')
    def action_get_attachment(self):
        logging.info('******************action_get_attachment***********************')
        logging.info(self.check_signature)
        for record in self:
            if record.check_signature == True:
                pdf = self.env.ref('sat_companies_sale.action_email_contract_signature')._render_qweb_pdf(self.ids)
                print(pdf)
                b64_pdf = base64.b64encode(pdf[0])
                record.pdf_file_sale_contract = b64_pdf
            else:
                record.pdf_file_sale_contract = False