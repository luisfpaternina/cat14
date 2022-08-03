# -*- coding: utf-8 -*-
from odoo import fields, models, api


class BimProject(models.Model):
    _inherit = "bim.project"

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', check_company=True,
                                     domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")


