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

    name = fields.Char('')
    state = fields.Selection([
        ('checking','Checking'),
        ('done','Done')],string="State", default='checking')
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
        string='Pit')
    check_pit = fields.Boolean(
        string='Pit')
    check_cabine = fields.Boolean(
        string='Cabine')
    check_machine = fields.Boolean(
        string='Machine')
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
                    record.state = 'done'
                else:
                    record.state = 'checking'


    def _generate_qr_code(self):
        base_url_pit = "pit,%d" % (self.id)
        print("***********************base_url_pit", base_url_pit)
        base_url_cabine = "cabine,%d" % (self.id)
        print("***********************base_url_cabine", base_url_cabine)
        base_url_machine = "machine,%d" % (self.id)
        print("***********************base_url_machine", base_url_machine)
        self.qr_pit = generate_qr_code(base_url_pit)
        self.qr_pit_image = generate_qr_code(base_url_pit)
        self.qr_cabine = generate_qr_code(base_url_cabine)
        self.qr_cabine_image = generate_qr_code(base_url_cabine)
        self.qr_machine = generate_qr_code(base_url_machine)
        self.qr_machine_image = generate_qr_code(base_url_machine)

    """
    def _generate_qr_code(self):
        base_url_home = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url_pit = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url_pit += "/product/qr-pit/check/%d" % (self.id)
        base_url_cabine = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url_cabine += "/product/qr-cabine/check/%d" % (self.id)
        base_url_machine = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url_machine += "/product/qr-machine/check/%d" % (self.id)
        self.qr_pit = generate_qr_code(base_url_pit)
        self.qr_pit_image = generate_qr_code(base_url_pit)
        self.qr_cabine = generate_qr_code(base_url_cabine)
        self.qr_cabine_image = generate_qr_code(base_url_cabine)
        self.qr_machine = generate_qr_code(base_url_machine)
        self.qr_machine_image = generate_qr_code(base_url_machine)
        self.url_home = base_url_home
    """


    def action_url(self):
        return {  
            'name': 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'self',
            'url'      : self.qr_scanner
            }
