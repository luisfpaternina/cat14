from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('bank_ids')
    def _check_exist_record_in_lines(self):
        for rec in self:
            exis_record_lines = []
            for line in rec.bank_ids:
                if line.is_default in exis_record_lines:
                    raise ValidationError(_('Solo se puede tener una cuenta bancaría por defecto!'))
                exis_record_lines.append(line.is_default)
