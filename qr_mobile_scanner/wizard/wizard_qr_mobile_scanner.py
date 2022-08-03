from odoo import models, fields, api

class WizardQrMobileScanner(models.TransientModel):
    _name = 'wizard.qr.mobile.scanner'

    name = fields.Char('')
    qr_scanner = fields.Char('Qr Scanner')
    check_qr_active = fields.Boolean('Check Qr')
    scanner = fields.Char(string="Scanner")
    
    @api.onchange('qr_scanner')
    def _onchange_qr_scanner(self):
        for record in self:
            if record.qr_scanner:
                record.check_qr_active = True
            else:
                record.check_qr_active = False

    def action_url(self):
        if self.check_qr_active == True:
            return {  
                'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type'     : 'ir.actions.act_url',
                'target'   : 'self',
                'url'      : self.qr_scanner
                }