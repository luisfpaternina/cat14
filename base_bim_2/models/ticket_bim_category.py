# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class TicketBimCategory(models.Model):
    _description = "Ticket Bim Category"
    _name = 'ticket.bim.category'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    @api.model
    def _needaction_domain_get(self):
        return [('name', '!=', '')]

    name = fields.Char('Name')
    email = fields.Char('Support Email')
