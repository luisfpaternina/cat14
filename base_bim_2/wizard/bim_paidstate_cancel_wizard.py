# coding: utf-8
from odoo import api, fields, models, _

from odoo.exceptions import RedirectWarning, UserError, ValidationError
class BimPaidstateWizard(models.TransientModel):
    _name = 'bim.paidstate.cancel.wizard'
    _description = 'Payment Status Cancel'

    def _default_paidstate_id(self):
        return self.env['bim.paidstate'].browse(self._context.get('active_id')).id

    paidstate_id = fields.Many2one('bim.paidstate', required=True, default=_default_paidstate_id)

    def process(self):
        self.paidstate_id.state = 'cancel'







