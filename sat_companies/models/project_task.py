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
        string="Is QR required?")
