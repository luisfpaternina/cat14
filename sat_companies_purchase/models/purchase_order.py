from odoo import models, fields, api, _
from datetime import datetime, date
import logging


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_type_id = fields.Many2one(
        'purchase.order.type',
        string="Purchase order type",
        tracking=True)
    is_validate_reception = fields.Boolean(
        string="Validate reception",
        tracking=True)
    is_validator = fields.Boolean(
        string="Validate")


    @api.depends('date_planned')
    def _compute_date_planned(self):
        now = datetime.now()
        for record in self:
            if record.date_planned:
                if record.date_planned >= now:
                    record.is_validate_reception = True
                else:
                    record.is_validate_reception = False
            else:
                record.is_validate_reception = False


    @api.onchange('date_planned','is_validate_reception')
    def _onchage_validate_reception(self):
        for record in self:
            if record.is_validate_reception:
                record.is_validator = True
            else:
                record.is_validator = False
