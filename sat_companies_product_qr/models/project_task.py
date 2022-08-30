from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import tzinfo, timedelta, datetime, date
from odoo.http import request
import base64
from io import BytesIO
import qrcode

class ProjectTask(models.Model):
    _inherit = 'project.task'
    

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        for record in self:
            if 'check_pit' in vals or 'check_cabine' in vals or 'check_machine' in vals :
                if record.check_pit == True and record.check_cabine == True and record.check_machine == True:
                    record.state_check_qr = 'done'
                else:
                    record.state_check_qr = 'checking'