# -*- coding: utf-8 -*-
##################################################################################################################################
#
# ING.LUIS FELIPE PATERNINA VITAL
#  
# Correo: lfpaternina93@gmail.com
#
#
# Celular: +573046079971 or +573215062353
#
# Bogotá,Colombia
#
###################################################################################################################################
from odoo import models, fields, api, _


class CancelLicensePlates(models.Model):

    _name = "cancel.license.plates"
    _inherit = 'mail.thread'
    _description = "Cancel license plates"

    name = fields.Char(
        string="Nombre",
        tracking=True)
    student_id = fields.Many2one(
        'students',
        string="Student")
