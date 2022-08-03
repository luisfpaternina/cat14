# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from datetime import datetime

class BimDocumentation(models.Model):
    _description = "Documentation BIM"
    _name = 'bim.documentation'
    _order = "id desc"
    _rec_name = 'desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Code', default="New", copy=False)
    desc = fields.Char('Description', copy=True)
    obs = fields.Text('Notes')
    project_id = fields.Many2one('bim.project', 'Project', ondelete="cascade", copy=True)
    user_id = fields.Many2one('res.users', string='Responsable', tracking=True,
        default=lambda self: self.env.user, copy=False)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company,
                                 required=True, copy=False)
    file_name = fields.Char("File Name", copy=False)
    file_01 = fields.Binary(string='File', copy=False)
    image_medium = fields.Binary("Image size", copy=False)

    def _set_image_medium(self):
        self._set_image_value(self.image_medium)

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.documentation') or "New"
        return super(BimDocumentation, self).create(vals)

    def print_document_notes(self):
        return self.env.ref('base_bim_2.notes_report_document').report_action(self)