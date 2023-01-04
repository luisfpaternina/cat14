# pylint: disable=missing-docstring
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models

DEFAULT_MESSAGE = "Default message"

SUCCESS = "success"
DANGER = "danger"
WARNING = "warning"
INFO = "info"
DEFAULT = "default"


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.depends("create_date")
    def _compute_channel_names(self):
        for record in self:
            res_id = record.id
            record.notify_success_channel_name = "notify_success_%s" % res_id
            record.notify_danger_channel_name = "notify_danger_%s" % res_id
            record.notify_warning_channel_name = "notify_warning_%s" % res_id
            record.notify_info_channel_name = "notify_info_%s" % res_id
            record.notify_default_channel_name = "notify_default_%s" % res_id

    notify_success_channel_name = fields.Char(compute="_compute_channel_names")
    notify_danger_channel_name = fields.Char(compute="_compute_channel_names")
    notify_warning_channel_name = fields.Char(compute="_compute_channel_names")
    notify_info_channel_name = fields.Char(compute="_compute_channel_names")
    notify_default_channel_name = fields.Char(compute="_compute_channel_names")
    play_alarm = fields.Boolean()

    def notify_success(
        self,
        message="Default message", title=None, subtitle=None,
        ref_ids=None, ref_model=None, sticky=False
    ):
        title = title or _("Success")
        self._notify_channel(SUCCESS, message, title, subtitle, ref_model, ref_ids, sticky)

    def notify_danger(
        self,
        message="Default message", title=None, subtitle=None,
        ref_ids=None, ref_model=None, sticky=False
    ):
        title = title or _("Danger")
        self._notify_channel(DANGER, message, title, subtitle, ref_model, ref_ids, sticky)

    def notify_warning(
        self,
        message="Default message", title=None, subtitle=None,
        ref_ids=None, ref_model=None, sticky=False
    ):
        title = title or _("Warning")
        self._notify_channel(WARNING, message, title, subtitle, ref_model, ref_ids, sticky)

    def notify_info(
        self,
        message="Default message", title=None, subtitle=None,
        ref_ids=None, ref_model=None, sticky=False):
        title = title or _("Information")
        self._notify_channel(INFO, message, title, subtitle, ref_model, ref_ids, sticky)

    def notify_default(
        self,
        message="Default message", title=None, subtitle=None,
        ref_ids=None, ref_model=None, sticky=False
    ):
        title = title or _("Default")
        self._notify_channel(DEFAULT, message, title, subtitle, ref_model, ref_ids, sticky)

    def _notify_channel(
        self,
        type_message=DEFAULT,
        message=DEFAULT_MESSAGE,
        title=None,
        subtitle=None,
        ref_model=None,
        ref_ids=None,
        sticky=False,
    ):
        # pylint: disable=protected-access
        channel_name_field = "notify_{}_channel_name".format(type_message)
        self.play_alarm = True
        bus_message = {
            "type": type_message,
            "message": message,
            "title": title,
            "subtitle": subtitle,
            "ref_ids": ref_ids,
            'ref_model': ref_model,
            "sticky": sticky,
        }
        notifications = [
            (record[channel_name_field], bus_message) for record in self
        ]
        self.env["bus.bus"].sendmany(notifications)
