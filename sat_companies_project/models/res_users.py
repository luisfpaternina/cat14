# pylint: disable=missing-docstring
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models



class ResUsers(models.Model):
    _inherit = "res.users"

    audio_notification_task = fields.Binary('Archivo de Alarma')