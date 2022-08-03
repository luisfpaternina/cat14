# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TicketBim(models.Model):
    _description = "Ticket Bim"
    _name = 'ticket.bim'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    @api.model
    def _needaction_domain_get(self):
        return [('state', '!=', 'resuelto')]

    name = fields.Char('Code', default="New", copy=False)
    title = fields.Char('Títle')
    obs = fields.Text('Observation')
    obs_solucion = fields.Text('Observation Solution')
    entry_date = fields.Datetime(
        'Entry Date', default=fields.Datetime.now)
    end_date = fields.Datetime('End Date')
    end_will_end = fields.Datetime('Expected date')
    user_id = fields.Many2one('res.users', string='Created',
                              default=lambda self: self.env.user)

    category_id = fields.Many2one('ticket.bim.category', string='Category')
    ticket_id = fields.Many2one('ticket.bim', string='Related Ticket')
    project_id = fields.Many2one('bim.project', 'Project', ondelete="cascade")

    numero_veces = fields.Integer('Number of times', default=1)

    user_error_id = fields.Many2one(
        'res.users', string='User', default=lambda self: self.env.user)

    user_work_id = fields.Many2one('res.users', string='Specialist')

    comprobante_01_name = fields.Char("Attachment Name")
    comprobante_01 = fields.Binary(
        string='Attachment',
        copy=False,
        help='Attachment')

    company_id = fields.Many2one(
        'res.company', string="Company", required=True,
        default=lambda self: self.env.user.company_id.id)

    state = fields.Selection([
        ('Draft', 'Draft'),
        ('aprobado', 'Approved'),
        ('trabajando', 'Working'),
        ('resuelto', 'Done'),
        ('calificado', 'Qualified')],
        string='Status', index=True, readonly=True, default='Draft',
        copy=False)

    clasificacion = fields.Selection([
        ('soporte', 'Support'),
        ('desarrollo', 'Development')],
        string='Classification', index=True, default='soporte', copy=False)

    calificacion = fields.Selection([
        ('0', 'Bad'),
        ('1', 'Regular'),
        ('2', 'Good'),
        ('3', 'Excellent')],
        string='Qualification', default='0', copy=False)

    obs_calificacion = fields.Text('Qualification Note')

    prioridad = fields.Selection(
        [('baja', 'Low'),
         ('media', 'Medium'),
         ('alta', 'High')], string='Priority',
        default='baja', copy=False)


    def exe_autorizar(self):
        for record in self:
            record.state = 'aprobado'
            """
            record.message_post(
                body=_("Ticket approved by: %s") % record.env.user.name)"""

    def exe_work(self):
        for record in self:
            record.user_work_id = record.env.user
            record.state = 'trabajando'
            record.message_post(
                body=_("Starting work: %s") % record.env.user.name)

    def exe_resuelto(self):
        for record in self:
            record.user_work_id = record.env.user
            record.state = 'resuelto'
            """
            record.message_post(body=_("Solution Note: %s") %
                                record.obs_solucion)
                                """
            record.end_date = fields.Datetime.now()

            """
            template = self.env.ref('ticket_pro.email_ticket_close')
            if record.comprobante_01:
                attachment = self.env['ir.attachment'].create({
                    'name': record.comprobante_01_name,
                    'datas': record.comprobante_01,
                    'datas_fname': record.comprobante_01_name,
                    'res_model': 'ticket.pro',
                    'type': 'binary'
                })
                template.attachment_ids = [(6, 0, attachment.ids)]
            mail = template.send_mail(record.id, force_send=True)  # envia mail
            if mail:
                record.message_post(
                    body=_("Aviso Ticket Terminado: %s" % record.category_id.name))"""

    def exe_abrir(self):
        for record in self:
            record.numero_veces = record.numero_veces + 1
            record.state = 'Draft'
            record.message_post(body=_("A new Open: %s") %
                                record.env.user.name)
            """
            template = self.env.ref('ticket_pro.email_ticket_pro_open')
            if self.comprobante_01:
                attachment = self.env['ir.attachment'].create({
                    'name': self.comprobante_01_name,
                    'datas': self.comprobante_01,
                    'datas_fname': self.comprobante_01_name,
                    'res_model': 'ticket.pro',
                    'type': 'binary'
                })
                template.attachment_ids = [(6, 0, attachment.ids)]
            mail = template.send_mail(self.id, force_send=True)  # envia mail
            if mail:
                self.message_post(
                    body=_("Enviado email a Soporte: %s" % self.category_id.name))
                    """

    def exe_close(self):
        if self.calificacion == '0':
            raise ValidationError(
                "Please rate our work so we can improve with your help, thank you very much.")
        for record in self:
            record.state = 'calificado'
            record.message_post(body=_("Qualified as: %s") %
                                record.calificacion)

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'ticket.bim') or "New"
        if 'category_id' not in vals:
            vals['category_id'] = self.env.ref('base_bim_2.ticket_proc_01').id
        ticket = super(TicketBim, self).create(vals)
        """
        template = self.env.ref('base_bim_2.email_ticket_pro')
        attachment = False
        if ticket.comprobante_01:
            attachment = self.env['ir.attachment'].create({
                'name': ticket.comprobante_01_name,
                'datas': ticket.comprobante_01,
                'datas_fname': ticket.comprobante_01_name,
                'res_model': 'ticket.pro',
                'type': 'binary'
            })
        template.attachment_ids = [
            (6, 0, attachment.ids)] if attachment else [(5,)]
        mail = template.send_mail(ticket.id, force_send=True)  # envia mail
        if mail:
            ticket.message_post(
                body=_("Enviado email a Soporte: %s" % ticket.category_id.name))
                """
        return ticket

