# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
from .qr_code_base import generate_qr_code
import base64
from io import BytesIO
import qrcode


class ProductQrGenerator(models.Model):
    _name = 'product.qr.generator'

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
        related="delegation.country_id.name",
        string="Name")
    from_gadget_location = fields.Char(
        related="from_gadget.location",
        string="Name")
    to_gadget_location = fields.Char(
        related="to_gadget.location",
        string="Name")
    from_zone_location = fields.Char(
        related="from_zone.name",
        string="Name")
    to_zone_location = fields.Char(
        related="to_zone.name",
        string="Name")
    qr_scanner = fields.Char(
        String = 'Pit')
    check_pit = fields.Boolean(
        String = 'Pit',
        tracking=True)
    check_cabine = fields.Boolean(
        String = 'Cabine',
        tracking=True)
    check_machine = fields.Boolean(
        String = 'Machine',
        tracking=True)
    qr_pit = fields.Binary(
        'Dowload Qr Image Pit',
        compute="_generate_qr_code")
    qr_pit_image = fields.Binary(
        'QR CODE IMAGE PIT',
        compute="_generate_qr_code")
    qr_cabine = fields.Binary(
        'Dowload QR Image Cabine',
        compute="_generate_qr_code")
    qr_cabine_image = fields.Binary(
        'QR CODE IMAGE CABINE',
        compute="_generate_qr_code")
    qr_machine = fields.Binary(
        'Dowload QR Image Machine',
        compute="_generate_qr_code")
    qr_machine_image = fields.Binary(
        'QR CODE IMAGE MACHINE',
        compute="_generate_qr_code")


    def write(self, vals):
        res = super(ProductQrGenerator, self).write(vals)
        for record in self:
            if 'check_pit' in vals or 'check_cabine' in vals or 'check_machine' in vals :
                if record.check_pit == True and record.check_cabine == True and record.check_machine == True:
                    record.state_check_qr = 'done'
                else:
                    record.state_check_qr = 'checking'


    def _generate_qr_code(self):
        base_url_pit = "pit,%d" % (self.id)
        base_url_cabine = "cabine,%d" % (self.id)
        base_url_machine = "machine,%d" % (self.id)
        self.qr_pit = generate_qr_code(base_url_pit)
        self.qr_pit_image = generate_qr_code(base_url_pit)
        self.qr_cabine = generate_qr_code(base_url_cabine)
        self.qr_cabine_image = generate_qr_code(base_url_cabine)
        self.qr_machine = generate_qr_code(base_url_machine)
        self.qr_machine_image = generate_qr_code(base_url_machine)


    def action_url(self):
        return {  
            'name': 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'self',
            'url'      : self.qr_scanner
            }
