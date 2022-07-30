import qrcode
from odoo import models, fields, api

class WizardQrMobileScannerInherit(models.TransientModel):
    _inherit = 'wizard.qr.mobile.scanner'

    id_product_qr_generator = fields.Integer(
        'Id product qr')
    qr_pit = fields.Boolean(
        'Qr Scanner Pit')
    qr_machine = fields.Boolean(
        'Qr Scanner Machine')
    qr_cabine = fields.Boolean(
        'Qr Scanner Cabine')
    check_from_product_qr = fields.Boolean(
        'check from product qr')

    @api.onchange('qr_scanner')
    def check_from_qr(self):
        for record in self:
            if record.qr_scanner:
                qr_data = record.qr_scanner.split(',')
                if qr_data[0] in ['pit','cabine','machine']:
                    record.check_from_product_qr = True
                else:
                    record.check_from_product_qr = False


    def action_check_product(self):
        for record in self:
            if record.qr_scanner:
                qr_data = record.qr_scanner.split(',')
                domain = ('id','=',qr_data[1])
                qr_product_model = self.env['product.qr.generator'].search([domain])
                if 'pit' in qr_data[0]:
                    record.qr_pit = True
                    record.qr_cabine = False
                    record.qr_machine = False
                    qr_product_model.check_pit = True
                    record.qr_scanner = False
                elif 'cabine' in qr_data[0]:
                    record.qr_cabine = True
                    record.qr_pit = False
                    record.qr_machine = False
                    qr_product_model.check_cabine = True
                    record.qr_scanner = False
                elif 'machine' in qr_data[0]:
                    record.qr_machine = True
                    record.qr_pit = False
                    record.qr_cabine = False
                    qr_product_model.check_machine = True
                    record.qr_scanner = False
                else:
                    record.qr_pit = False
                    record.qr_cabine = False
                    record.qr_machine = False
                    record.qr_scanner = False

    """
    def check_product_devices(self):
        for record in self:
            if record.qr_scanner:
                qr_data = record.qr_scanner.split(',')
                domain = ('id','=',qr_data[1])
                qr_product_model = self.env['product.qr.generator'].search([domain])
                if 'pit' in qr_data[0]:
                    qr_product_model.check_pit = True
                elif 'cabine' in qr_data[0]:
                    qr_product_model.check_cabine = True
                elif 'machine' in qr_data[0]:
                    qr_product_model.check_ = True
    """
