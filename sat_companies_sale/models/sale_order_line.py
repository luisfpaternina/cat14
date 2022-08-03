# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    rae = fields.Char(
        string="R.A.E.")
    ref = fields.Char(
        string="Reference")
    maneuver = fields.Char(
        string="Maneuver")
    elevator_type_id = fields.Many2one(
        'stock.elevator.type',
        string="Elevator type")
    people_numbers = fields.Char(
        string="People numbers")
    gadget_load = fields.Char(
        string="Load(Kgs)")
    nominal_speed = fields.Char(
        string="Nominal speed(m/s)")
    check_is_gadget = fields.Boolean(
        related='product_id.is_gadget')


    @api.onchange('product_id')
    def product_gadget_domain(self):
        for record in self:
            if record.order_id.product_id.is_gadget == True:
                return {'domain': {'product_id': [('is_gadget', '=', False)]}}
