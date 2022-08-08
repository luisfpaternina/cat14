# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
import qrcode


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_qr_required = fields.Boolean(
        string="Is QR required?",
        compute="compute_is_required_qr")
    check_pit = fields.Boolean(
        string = 'Pit', tracking=True)
    check_cabine = fields.Boolean(
        string = 'Cabine', tracking=True)
    check_machine = fields.Boolean(
        string = 'Machine', tracking=True)


    @api.depends('name','partner_id')
    def compute_is_required_qr(self):
        qr_required = self.env['ir.config_parameter'].sudo().get_param('sat_companies.is_qr_required') or False
        self.is_qr_required = qr_required

    @api.constrains('partner_id','name')
    def _is_qr_required(self):
        for record in self:
            if not record.check_pit:
                if record.is_qr_required:
                    raise ValidationError(_(
                        'It is necessary to scan at least one qr code'))
            elif not record.check_cabine:
                if record.is_qr_required:
                    raise ValidationError(_(
                        'It is necessary to scan at least one qr code'))
            elif not record.check_machine:
                if record.is_qr_required:
                    raise ValidationError(_(
                        'It is necessary to scan at least one qr code'))

