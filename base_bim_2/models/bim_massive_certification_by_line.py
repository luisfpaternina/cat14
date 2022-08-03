# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BimMasCertification(models.Model):
    _name = 'bim.massive.certification.by.line'
    _description = 'Massive Certification'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    name = fields.Char(string='Sequence',required=True,  default=_('New'), copy=False)
    user_id = fields.Many2one('res.users', string='Responsable', readonly=True, index=True, tracking=True,
                              required=True,
                              default=lambda self: self.env.user)
    type = fields.Selection([('current_stage','Current Stage'),('fixed','Manual')], string='Certification Type',required=True, default='current_stage', readonly=True)
    state = fields.Selection([('draft','Draft'),('ready','Ready'),('done','Done'),('cancelled','Cancelled')], tracking=True, default='draft', string='Status',required=True)
    project_id = fields.Many2one('bim.project', string='Project', required=True, domain="[('company_id','=',company_id)]")
    budget_id = fields.Many2one('bim.budget', string='Budget', required=True, domain="[('project_id', '=', project_id)]")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True, readonly=True)
    certification_date = fields.Date(string='Certification Date', readonly=True, index=True, copy=False, default=fields.Date.context_today)
    creation_date = fields.Date(string='Creation Date', readonly=True, index=True, copy=False, default=fields.Date.context_today)
    note = fields.Text(copy=False)
    certification_stage_ids = fields.Many2many('bim.certification.stage.certification', 'certification_line_rel', string='Certification', copy=False)
    concept_ids = fields.Many2many('bim.certification.fixed.certification','certification_fixed_rel', string='Measurement', copy=False)
    total_certif = fields.Float(string='Balance Certif.', compute='_compute_total_certif')
    percent_certif = fields.Float(string='(%) Certif.', compute='_compute_total_certif')
    greater_than_100 = fields.Boolean(string='(%) >= 100', default=True)

    def fix_certification_by_stage(self):
        for line in self.certification_stage_ids:
            line.amount_cert = line.concept_id.amount_compute_cert

    @api.depends('concept_ids.amount_certif','certification_stage_ids.amount_certif')
    def _compute_total_certif(self):
        for record in self:
            amount = 0
            if record.type == 'current_stage':
                for line in record.certification_stage_ids:
                    amount += line.amount_certif
            else:
                for line in record.concept_ids:
                    amount += line.amount_certif
            record.total_certif = amount
            record.percent_certif = record.total_certif / record.budget_id.balance * 100 if record.budget_id.balance > 0 else 0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.massive.certification') or _('New')
        res = super(BimMasCertification, self).create(vals)
        if not res.budget_id.stage_ids and res.type == 'current_stage':
            raise UserError(_("Yo can not create a certification if the Project does not have Stages created. Please generate some Project Stages and try again."))
        res._validate_current_stage()
        return res

    def _validate_current_stage(self):
        for record in self:
            current_stage = record.budget_id.stage_ids.filtered_domain([('state', '=', 'process')])
            if not current_stage and record.type == 'current_stage':
                raise UserError(
                    _("It is not possible use Current Stage mode because there is not current stage in this budget."))

    def action_ready(self):
        if self.type == 'current_stage':
            if not self.stage_id:
                raise UserError(_('You must select the Stage to Certify'))
        self.state = 'ready'

    def action_cancel(self):
        self.state='cancelled'

    def action_convert_to_draft(self):
        self.state='draft'

    def action_load_lines(self):
        if self.type == 'current_stage':
            self.load_line_by_stage('process')
        else:
            self.load_line_by_fixed()
        self.state = 'ready'

    def load_line_by_stage(self, stage):
        for record in self:
            for line in record.certification_stage_ids:
                line.unlink()
            certification_lines = []
            error = False
            record._validate_current_stage()

            sorted_concepts = sorted(record.budget_id.concept_ids, key=lambda s: s.parent_id.id)
            if not self.greater_than_100:
                concept_list = []
                for concp in sorted_concepts:
                    if concp.percent_cert < 100:
                        concept_list.append(concp)
                sorted_concepts = concept_list
            for concept in sorted_concepts:
                if concept.type == 'departure' and concept.parent_id.type == 'chapter':
                    if concept.quantity_cert > 0:
                        if concept.type_cert == 'stage':
                            for cert_stage in concept.certification_stage_ids:
                                if cert_stage.stage_id.state == stage:
                                    vals = {
                                        'certification_line_id': cert_stage.id,
                                        'budget_qty': concept.quantity,
                                        'amount_cert': concept.amount_compute_cert,
                                        'stage_id': cert_stage.stage_id.id,
                                        'certif_qty': cert_stage.certif_qty,
                                        'concept_id': cert_stage.concept_id.id,
                                        'amount_budget': concept.balance,
                                        'parent_id': cert_stage.concept_id.parent_id.id,
                                        'percent_acc': concept.percent_cert,
                                    }
                                    certification_lines.append((0, 0, vals))
                        else:
                            error = True
                    else:
                        concept.type_cert = 'stage'
                        concept.generate_stage_list()
                        for cert_stage in concept.certification_stage_ids:
                            if cert_stage.stage_id.state == stage:
                                vals = {
                                    'certification_line_id': cert_stage.id,
                                    'budget_qty': concept.quantity,
                                    'amount_cert': concept.amount_compute_cert,
                                    'stage_id': cert_stage.stage_id.id,
                                    'certif_qty': cert_stage.certif_qty,
                                    'concept_id': cert_stage.concept_id.id,
                                    'amount_budget': concept.balance,
                                    'parent_id': cert_stage.concept_id.parent_id.id,
                                    'percent_acc': concept.percent_cert,
                                }
                                certification_lines.append((0, 0, vals))

            if error and len (certification_lines) == 0:
                raise UserError(_('Certification by Stage is not possible because this Budget has all its items certified by Manual Way'))
            record.certification_stage_ids = certification_lines

    def load_line_by_fixed(self):
        for record in self:
            error = False
            for line in record.concept_ids:
                line.unlink()
            certification_lines = []
            sorted_concepts = sorted(record.budget_id.concept_ids, key=lambda s: s.parent_id.id)
            if not self.greater_than_100:
                concept_list = []
                for concp in sorted_concepts:
                    if concp.percent_cert < 100:
                        concept_list.append(concp)
                sorted_concepts = concept_list
            for concept in sorted_concepts:
                if concept.type == 'departure' and concept.parent_id.type == 'chapter':
                    if concept.quantity_cert > 0:
                        if concept.type_cert == 'fixed':
                            vals = {
                                'concept_id': concept.id,
                                'balance': concept.balance,
                                'quantity_cert': concept.quantity_cert,
                                'amount_cert': concept.amount_compute_cert,
                                'quantity': concept.quantity,
                                'percent_acc': concept.percent_cert,
                            }
                            certification_lines.append((0, 0, vals))
                        else:
                            error = True
                    else:
                        concept.type_cert = 'fixed'
                        vals = {
                            'concept_id': concept.id,
                            'balance': concept.balance,
                            'quantity_cert': concept.quantity_cert,
                            'amount_cert': concept.amount_compute_cert,
                            'quantity': concept.quantity,
                            'percent_acc': concept.percent_cert,
                        }
                        certification_lines.append((0, 0, vals))
            if error and len (certification_lines) == 0:
                raise UserError(_('Manual certification is not possible because this Budget has all its items certified by Stage'))
            record.concept_ids = certification_lines

    def action_massive_certification(self):
        if self.type =='current_stage':
            self.certify_by_stage()
        else:
            self.certify_by_fixed()
        self.state = 'done'

    def action_fix(self):
        if self.type =='current_stage':
            self.rectify_by_stage()
        else:
            self.rectify_by_fixed()
        self.state = 'ready'

    def certify_by_stage(self):
        for line in self.certification_stage_ids:
            line.certification_line_id.certif_qty = line.certification_line_id.certif_qty + line.quantity_to_cert
            line.certification_line_id.certif_percent = line.certification_line_id.certif_percent + line.certif_percent
            line.certification_line_id.onchange_percent()
            line.certification_line_id.onchange_qty()
            line.concept_id.onchange_percent_certification()
            line.concept_id.onchange_qty_certification()
            if line.certif_percent > 0:
                line.concept_id._compute_check_percent_certification()

    def certify_by_fixed(self):
        for line in self.concept_ids:
            line.concept_id.update_budget_type()
            line.concept_id.quantity_cert = line.concept_id.quantity_cert + line.quantity_to_cert
            line.concept_id.percent_cert = line.concept_id.percent_cert + line.percent_cert
            if line.percent_cert > 0:
                line.concept_id._compute_check_percent_certification()

    def rectify_by_stage(self):
        for line in self.certification_stage_ids:
            if line.stage_id.state == 'approved':
                raise UserError(_('It is not possible to Undo this Certification because it contains an Approved Stage'))
            line.certification_line_id.certif_qty = line.certification_line_id.certif_qty - line.quantity_to_cert if (line.certification_line_id.certif_qty - line.quantity_to_cert) >= 0 else 0
            line.certification_line_id.certif_percent = line.certification_line_id.certif_percent - line.certif_percent if(line.certification_line_id.certif_percent - line.certif_percent) >= 0 else 0
            line.certification_line_id.onchange_percent()
            line.concept_id.onchange_percent_certification()
            line.concept_id.onchange_qty_certification()
            line.quantity_to_cert = 0
            line.certif_percent = 0

    def rectify_by_fixed(self):
        for line in self.concept_ids:
            line.concept_id.quantity_cert = line.concept_id.quantity_cert - line.quantity_to_cert if (line.concept_id.quantity_cert - line.quantity_to_cert) > 0 else 0
            line.concept_id.percent_cert = line.concept_id.percent_cert - line.percent_cert if (line.concept_id.percent_cert - line.percent_cert) >= 0 else 0
            line.quantity_to_cert = 0
            line.percent_cert = 0

    def unlink(self):
        for record in self:
            if record.state == 'done':
                raise UserError(_('It is not possible to delete an Applied Certification. You must first Undo it and then Delete it'))
        return super(BimMasCertification, self).unlink()


class BimCertificationFixedCertification(models.Model):
    _name = 'bim.certification.fixed.certification'
    _description = "Manual Certification"

    @api.depends('quantity_to_cert')
    def _compute_amount(self):
        for record in self:
            record.amount_certif = record.quantity_to_cert * record.amount_cert
            record.percent_cert = record.quantity_to_cert / record.quantity * 100 if record.quantity else 0

    @api.onchange('percent_cert')
    def onchange_percent_cert(self):
        for record in self:
            record.quantity_to_cert = record.percent_cert * record.quantity / 100 if (record.percent_cert * record.quantity) > 0 else 0

    parent_id = fields.Many2one(string='Chapter', related='concept_id.parent_id', required=True)
    name = fields.Char(string='Name', related='concept_id.display_name', required=True)
    quantity_cert = fields.Float(string='Accumulated Cert', default=0, digits='BIM qty')
    percent_acc = fields.Float(string='(%) Accumulated', default=0, digits='BIM qty')
    quantity_to_cert = fields.Float(string='Quant Cert', default=0, digits='BIM qty')
    percent_cert = fields.Float(string='(%) Cert Budget', default=0, digits='BIM price')
    concept_id = fields.Many2one('bim.concepts', "Budget Item")
    balance = fields.Float(string='Total Budget', digits='BIM price')
    amount_certif = fields.Float(string='Balance Cert', digits='BIM price', compute='_compute_amount', tracking=True, store=True)
    amount_cert = fields.Float(string='Price Cert', digits='BIM price')
    quantity = fields.Float(string='Quant Budget(N)', digits='BIM price')


class BimCertificationStageCertification(models.Model):
    _name = 'bim.certification.stage.certification'
    _description = "Stage Certification"

    @api.depends('stage_id', 'stage_id.state', 'budget_qty', 'quantity_to_cert','certif_percent')
    def _compute_amount(self):
        for record in self:
                record.amount_certif = record.quantity_to_cert * record.amount_cert

    certification_line_id = fields.Many2one('bim.certification.stage')
    name = fields.Date(string='Date', related='certification_line_id.name', required=True)
    certif_qty = fields.Float(string='Accumulated Cert', default=0, digits='BIM qty')
    budget_qty = fields.Float(string='Quant Budget (N)', default=0, digits='BIM qty')
    quantity_to_cert = fields.Float(string='Quant Cert (N)', default=0, digits='BIM qty')
    certif_percent = fields.Float(string='(%) Cert', default=0, digits='BIM price')
    stage_id = fields.Many2one('bim.budget.stage', "Stage", related='certification_line_id.stage_id')
    concept_id = fields.Many2one('bim.concepts', "Budget Item", related='certification_line_id.concept_id')
    amount_budget = fields.Float(string='Total Budget', digits='BIM price')
    amount_certif = fields.Float(string='Balance Cert', digits='BIM price', compute="_compute_amount", tracking=True, store=True)
    parent_id = fields.Many2one('bim.concepts', string="Chapter")
    percent_acc = fields.Float(string='(%) Accumulated', default=0, digits='BIM qty')
    balance = fields.Float(string='Total Budget', digits='BIM price')
    amount_cert = fields.Float(string='Price Cert', digits='BIM price')

    @api.onchange('quantity_to_cert')
    def onchange_qty(self):
        for record in self:
            if record.budget_qty <= 0:
                record.certif_percent = (record.quantity_to_cert / 1) * 100
            else:
                record.certif_percent = (record.quantity_to_cert / record.budget_qty) * 100

    @api.onchange('certif_percent')
    def onchange_percent(self):
        for record in self:
            record.quantity_to_cert = (record.budget_qty * record.certif_percent) / 100

    def action_next(self):
        if self.stage_state == 'draft':
            self.stage_id.state = 'process'
        elif self.stage_state == 'process':
            self.stage_id.state = 'approved'

    def action_cancel(self):
        return self.stage_id.write({'state': 'cancel'})

