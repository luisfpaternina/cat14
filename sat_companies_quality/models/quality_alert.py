from odoo import models, fields, api, _
from datetime import datetime, date


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    nonconformity_date = fields.Date(
        string="Nonconformity date")
    nonconformity_number = fields.Char(
        string="Nonconformity number")
    is_audit = fields.Boolean(
        string="Is audit")
    is_process = fields.Boolean(
        string="Is process")
    is_documentary = fields.Boolean(
        string="Is documentary")
    is_purchases_suppliers = fields.Boolean(
        string="Purchases and suppliers")
    is_complaints = fields.Boolean(
        string="Is complaints")
    nonconformity_description = fields.Text(
        string="Description")
    nonconformity_causes = fields.Text(
        string="Causes")
    detected_by = fields.Char(
        string="Detected by")
    detected_date = fields.Date(
        string="Detected date")
    immediate_solution = fields.Text(
        string="Immediate solution")
    is_indicators = fields.Boolean(
        string="Is indicators")
    user_execution_id = fields.Many2one(
        'res.users',
        string="Responsible execution")
    execution_period = fields.Char(
        string="Execution period")
    closing_date = fields.Date(
        string="Closing date")
    risks_opportunities = fields.Boolean(
        string="Risks and opportunities")
    responsable_sign = fields.Binary(
        string="Responsable sign")
    is_corrective_action = fields.Boolean(
        string="Is corrective action")
    quality_responsable_sign = fields.Binary(
        string="Quality responsable sign")
    actions_carried_out =fields.Text(
        string="Actions to be carried out")
    user_carried_id = fields.Many2one(
        'res.users',
        string="Carried out responsable")
    term = fields.Char(
        string="Term")
    monitoring_verification = fields.Text(
        string="Monitoring and verification")
    quality_responsable = fields.Binary(
        string="Quality responsable sign")
    quality_date = fields.Date(
        string="Quality date")
