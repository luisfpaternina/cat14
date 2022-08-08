import calendar
from odoo.tools import formatLang
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _


class ProdctStoppedWizard(models.TransientModel):
    _name = "product.stopped.wizard"
    _description = "Gadget stopped"

    stop_reason_id = fields.Many2one(
        'gadget.stop.reason',
        string="Reason")
    product_id = fields.Many2one(
        'product.template',
        string="Gadget")
    

    def gadget_stopped_confirm(self):
        product_obj =  self.env['product.template'].search([('id','=',self.product_id.id)])
        if product_obj:
            product_obj.write({
                'is_gadget_stopped': True, 
                'stop_reason_id': self.stop_reason_id.id
                })
