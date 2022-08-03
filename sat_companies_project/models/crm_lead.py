# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from operator import rshift
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class Opportunity2Quotation(models.Model):
    _inherit = 'crm.lead'


    def action_new_quotation(self):
        result = super(Opportunity2Quotation, self).action_new_quotation()
        if result.get('id'):
            vals = {
                'default_udn_id': self.udn_type_id.id,
                'default_sale_type_id': self.sale_type_id.id,
            }
        
            result.get('context').update(vals)
        return result
