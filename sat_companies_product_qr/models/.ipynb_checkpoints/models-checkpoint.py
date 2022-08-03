# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
import qrcode
import logging


class ProductQrGenerator(models.Model):
    _name = 'product.qr.generator'
    
    name = fields.Char('')
    state = fields.Selection([
        ('checking','Checking'),
        ('done','Done')],string="State", default='checking', tracking=True)
    
    delegation = fields.Many2one('res.partner.delegation', string="Delegation")
    from_gadget = fields.Many2one('stock.gadgets', string="From the Gadget")
    to_gadget = fields.Many2one('stock.gadgets', string="To the Gadget")
    from_zone = fields.Many2one('res.partner.zones', string="From the Zone")
    to_zone = fields.Many2one('res.partner.zones', string="To the Zone")
    
    delegation_location = fields.Char(related="delegation.country_id.name",
                                     string="Country")
    from_gadget_location = fields.Char(related="from_gadget.location",
                                      string="Locatoin")
    to_gadget_location = fields.Char(related="to_gadget.location",
                                     string="Location")
    from_zone_location = fields.Char(related="from_zone.code",
                                    string="Code")
    to_zone_location = fields.Char(related="to_zone.code",
                                  string="Code")
    
    check_pit = fields.Boolean(String = 'Pit', tracking=True)
    check_cabin = fields.Boolean(String = 'Cabin', tracking=True)
    check_machine = fields.Boolean(String = 'Machine', tracking=True)
    
    product_pit_qr_code = fields.Char('QR Code Pit')
    qr_code_pit = fields.Binary('QR Code Image Pit')
    qr_code_pit_name = fields.Char(default="qr_code_pit.png")
    
    product_cabin_qr_code = fields.Char('QR Code Cabin')
    qr_code_cabin = fields.Binary('QR Code Image Cabin')
    qr_code_cabin_name = fields.Char(default="qr_code_cabin.png")
    
    product_machine_qr_code = fields.Char('QR Code Machine')
    qr_code_machine = fields.Binary('QR Code Image Machine')
    qr_code_machine_name = fields.Char(default="qr_code_machine.png")
    
    def write(self, vals):
        res = super(ProductQrGenerator, self).write(vals)
        for record in self:
            if 'check_pit' in vals or 'check_cabin' in vals or 'check_machine' in vals :
                logging.info(record.check_pit)
                logging.info(record.check_cabin)
                logging.info(record.check_machine)
                if record.check_pit == True and record.check_cabin == True and record.check_machine == True:
                    record.state = 'done'
                else:
                    record.state = 'checking'



    @api.onchange('product_pit_qr_code')
    def action_generate_qr(self):
        for record in self:
            if record.product_pit_qr_code:
                qr_pit = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=50, border=4)
                qr_cabin = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=50, border=4)
                qr_machine = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=50, border=4)
                name_pit = record.product_pit_qr_code + '_pit.png'
                name_cabin = record.product_cabin_qr_code + '_cabin.png'
                name_machine = record.product_machine_qr_code + '_machine.png'
                qr_pit.add_data(record.product_pit_qr_code)
                qr_cabin.add_data(record.product_cabin_qr_code)
                qr_machine.add_data(record.product_machine_qr_code)
                qr_pit.make(fit=True)
                qr_cabin.make(fit=True)
                qr_machine.make(fit=True)
                img_pit = qr_pit.make_image()
                img_cabin = qr_cabin.make_image()
                img_machine = qr_machine.make_image()
                buffer_pit = BytesIO()
                buffer_cabin = BytesIO()
                buffer_machine = BytesIO()
                img_pit.save(buffer_pit, format="PNG")
                img_cabin.save(buffer_cabin, format="PNG")
                img_machine.save(buffer_machine, format="PNG")
                qrcode_pit_img = base64.b64encode(buffer_pit.getvalue())
                qrcode_cabin_img = base64.b64encode(buffer_cabin.getvalue())
                qrcode_machine_img = base64.b64encode(buffer_machine.getvalue())
                record.update({'qr_code_cabin': qrcode_cabin_img,
                               'qr_code_cabin_name': name_cabin,
                               'qr_code_pit': qrcode_pit_img,
                               'qr_code_pit_name': name_pit,
                               'qr_code_machine': qrcode_machine_img,
                               'qr_code_machine_name': name_machine})
            else:
                record.product_pit_qr_code = "pit_" + str(record.id)
                record.product_cabin_qr_code = "cabin_" + str(record.id)
                record.product_machine_qr_code = "machine_" + str(record.id)
                qr_pit = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=50, border=4)
                qr_cabin = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=50, border=4)
                qr_machine = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=50, border=4)
                name_pit = record.product_pit_qr_code + '_pit.png'
                name_cabin = record.product_cabin_qr_code + '_cabin.png'
                name_machine = record.product_machine_qr_code + '_machine.png'
                qr_pit.add_data(record.product_pit_qr_code)
                qr_cabin.add_data(record.product_cabin_qr_code)
                qr_machine.add_data(record.product_machine_qr_code)
                qr_pit.make(fit=True)
                qr_cabin.make(fit=True)
                qr_machine.make(fit=True)
                img_pit = qr_pit.make_image()
                img_cabin = qr_cabin.make_image()
                img_machine = qr_machine.make_image()
                buffer_pit = BytesIO()
                buffer_cabin = BytesIO()
                buffer_machine = BytesIO()
                img_pit.save(buffer_pit, format="PNG")
                img_cabin.save(buffer_cabin, format="PNG")
                img_machine.save(buffer_machine, format="PNG")
                qrcode_pit_img = base64.b64encode(buffer_pit.getvalue())
                qrcode_cabin_img = base64.b64encode(buffer_cabin.getvalue())
                qrcode_machine_img = base64.b64encode(buffer_machine.getvalue())
                record.update({'qr_code_cabin': qrcode_cabin_img,
                               'qr_code_cabin_name': name_cabin,
                               'qr_code_pit': qrcode_pit_img,
                               'qr_code_pit_name': name_pit,
                               'qr_code_machine': qrcode_machine_img,
                               'qr_code_machine_name': name_machine})