# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : MadeUp Infotech (<https://www.madeupinfotech.com/>)
# Copyright(c): 2016-Present MadeUp Infotech
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

class ImBus(models.Model):
    _inherit = 'bus.bus'

    @api.model
    def poll(self, channels, last=0, options=None):
        res = super(ImBus, self).poll(channels, last, options)
        notifications = []
        for notification in res:
            if notification['channel'] == "notify":
                ids = notification['message']['ids']
                del notification['message']['ids']
                for channel in channels:
                    if isinstance(channel, tuple) and 'res.partner' in channel:
                        user_id = self.env['res.users'].sudo().search([('partner_id', '=', channel[2])])
                        if user_id.id in ids:
                            notifications.append(notification)
            else:
                notifications.append(notification)
        return notifications
