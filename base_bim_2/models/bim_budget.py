import base64
import io
from datetime import date, datetime, timedelta
import re
from io import BytesIO
from dateutil.relativedelta import relativedelta
import logging

import xlwt
from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from werkzeug.urls import url_encode

_logger = logging.getLogger(__name__)

try:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except (ImportError, IOError):
    plt = False
    _logger.warning('Missing external dependency matplotlib.')

inconsistency = {
    '0': _('No inconsistencies were found in the Budget.'),
    '1': _('-Resource %s has no Product assigned (Concept Error).'),
    '2': _('-Product %s, assigned to Resource %s, is not of Material Resource Type (Product Error).'),
    '3': _('-Product %s, assigned to Resource %s, is not of Type Resource Equipment (Product Error).'),
    '4': _('-Product %s, assigned to Resource %s, is not of Type Resource Labor (Product Error).'),
    '5': _('-Product %s, assigned to Resource %s, is a Service (Product Error).'),
    '6': _('-Product %s, assigned to Resource %s, is Storable (Product Error).'),
    '7': _('-Resource %s amount is zero (0).'),
    '8': _('-Chapter %s has quantity greater than 1.'),
    '9': _('-Resource %s has Child assigned (Concept Error).'),
    '10': _('-UoM of Resource %s is different than UoM of related Product %s. (Parent %s)'),
}
class BimBudgetState(models.Model):
    _name = 'bim.budget.state'
    _description = 'Bim Budget State'
    _order = "sequence asc, id desc"

    name = fields.Char(required=True, translate=True)
    is_new = fields.Boolean()
    include_in_amount = fields.Boolean(string="Include in amount", default=True)
    is_done = fields.Boolean()
    sequence = fields.Integer(default=16)
    user_ids = fields.Many2many('res.users', string="Users")

class BimBudget(models.Model):
    _name = 'bim.budget'
    _description = 'Budgets'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, fields):
        values = super().default_get(fields)
        if 'project_id' in values:
            project = self.env['bim.project'].browse(values['project_id'])
            if project.cost_list_id:
                values['cost_list_id'] = project.cost_list_id.id
        return values

    @api.depends('concept_ids.balance')
    def _compute_amount(self):
        for budget in self:
            balance = 0
            certified = 0
            for concept in budget.concept_ids:
                if not concept.parent_id:
                    balance += concept.balance
                    certified += concept.balance_cert
            budget.balance = balance
            budget.certified = certified

    @api.depends('concept_ids')
    def _compute_execute(self):
        for budget in self:
            concept_ids = budget.concept_ids.ids

            concepts = budget.concept_ids
            equipments = concepts.filtered(lambda c: c.type == 'equip')
            materials = concepts.filtered(lambda c: c.type == 'material')
            labors = concepts.filtered(lambda c: c.type == 'labor')
            functions = concepts.filtered(lambda c: c.type == 'aux')
            departures = concepts.filtered(lambda c: c.type == 'departure')

            budget.amount_executed_equip = sum(e.amount_execute_equip for e in departures)
            budget.amount_executed_labor = sum(l.amount_execute_labor for l in departures)
            budget.amount_executed_material = sum(m.amount_execute_material for m in departures)
            budget.amount_executed_other = sum(f.amount_execute for f in functions)

    def _get_value(self, quantity, product):
        if product.cost_method == 'fifo':
            quantity = product.quantity_svl
            if float_is_zero(quantity, precision_rounding=product.uom_id.rounding):
                value = 0.0
            average_cost = product.value_svl / quantity
            value = quantity * average_cost
        else:
            value = quantity * product.standard_price
        return float(value)

    def recursive_certified(self, resource, parent, amount=None):
        amount = amount is None and resource.balance_cert or amount or 0.0
        if parent.parent_id.type == 'departure':
            amount_partial = amount * parent.quantity_cert
            return self.recursive_amount(resource,parent.parent_id,amount_partial)
        else:
            return amount * parent.quantity_cert

    def recursive_amount(self, resource, parent, amount=None):
        amount = amount is None and resource.balance or amount or 0.0
        if parent.type == 'departure':
            amount_partial = amount * parent.quantity
            return self.recursive_amount(resource,parent.parent_id,amount_partial)
        else:
            return amount * parent.quantity

    def get_total(self,resource_id):
        records = self.concept_ids.filtered(lambda c: c.product_id.id == resource_id)
        total = 0
        for rec in records:
            total += rec.recursive_amount(rec,rec.parent_id,None)
        return total


    @api.depends('balance','certified','concept_ids.balance')
    def _get_amount_total(self):
        for budget in self:
            concepts = budget.concept_ids
            equipments = concepts.filtered(lambda c: c.type == 'equip')
            materials = concepts.filtered(lambda c: c.type == 'material')
            labors = concepts.filtered(lambda c: c.type == 'labor')
            functions = concepts.filtered(lambda c: c.type == 'aux')

            budget.amount_total_equip = sum(budget.get_total(e.id) for e in equipments.mapped('product_id'))
            budget.amount_total_labor = sum(budget.get_total(l.id) for l in labors.mapped('product_id'))
            budget.amount_total_material = sum(budget.get_total(m.id) for m in materials.mapped('product_id'))
            budget.amount_total_other =  sum(budget.recursive_amount(f,f.parent_id,None) for f in functions)

            budget.amount_certified_equip = sum(e.balance_cert for e in equipments)     #sum(self.recursive_certified(e,e.parent_id,None) for e in equipments)   #
            budget.amount_certified_labor = sum(l.balance_cert for l in labors)         #sum(self.recursive_certified(l,l.parent_id,None) for l in labors)       #
            budget.amount_certified_material = sum(m.balance_cert for m in materials)      #sum(self.recursive_certified(m,m.parent_id,None) for m in materials) #
            budget.amount_certified_other =   sum(f.balance_cert for f in functions)      #sum(self.recursive_certified(f,f.parent_id,None) for f in functions)  #

    @api.model
    def create(self, vals):
        if vals.get('code', "New") == "New":
            vals['code'] = self.env['ir.sequence'].next_by_code('bim.budget') or "New"
            vals['space_ids'] = [(0, 0, {'name': vals['code'],'code': 'S1'})]
        budget = super(BimBudget, self).create(vals)

        # if not vals.get('template_id'):
        #     template = self.env.company.asset_template_id
        #     self._create_assets(template)

        return budget

    def write(self, vals):
        res = super(BimBudget, self).write(vals)
        if 'type' in vals:
            for concept in self.concept_ids:
                concept.update_budget_type()
        return res

    @api.depends('project_id')
    def _compute_surface(self):
        for budget in self:
            budget.surface = 0

    @api.depends('concept_ids')
    def _get_concept_count(self):
        for budget in self:
            budget.concept_count = len(budget.concept_ids)

    @api.depends('stage_ids')
    def _get_stage_count(self):
        for budget in self:
            budget.stage_count = len(budget.stage_ids)

    @api.depends('space_ids')
    def _get_space_count(self):
        for budget in self:
            budget.space_count = len(budget.space_ids)

    @api.depends('concept_ids')
    def _compute_balance_surface(self):
        for record in self:
            concepts = record.env['bim.concepts'].search([('budget_id', '=', record.id),('parent_id', '=', False)])
            total = 0.0
            for concept in concepts:
                total += concept.balance
            if record.surface != 0:
                balace_surface = total / record.surface
            else:
                balace_surface = 0.0
            record.balace_surface = balace_surface

    name = fields.Char('Description', required=True, index=True)
    code = fields.Char('Code', required=True, index=True, default="New")
    note = fields.Text('Summary', copy=True)
    balace_surface = fields.Monetary(string="Amount /m2", compute=_compute_balance_surface, help="Amount per m2")
    balance = fields.Monetary(string="Amount", compute='_compute_amount', help="General Amount of the Budget.")
    certified = fields.Monetary(string="Certified", compute='_compute_amount', help="Certified Budget Amount.")
    surface = fields.Float(string="Surface m2", help="Builded surface (m2).", copy=True)
    project_id = fields.Many2one('bim.project', string='Project', tracking=True, ondelete='restrict')
    analysis_graph = fields.Binary(readonly=True)

    template_id = fields.Many2one('bim.assets.template',
                                  copy=False,
                                  string='Template',
                                  tracking=True)
    # default=lambda self: self.env.company.asset_template_id.id,
    user_id = fields.Many2one('res.users', string='Responsable', tracking=True, default=lambda self: self.env.user)
    indicator_ids = fields.One2many('bim.budget.indicator', 'budget_id', 'Comparative indicators')
    concept_ids = fields.One2many('bim.concepts', 'budget_id', 'Concept', tracking=True)
    stage_ids = fields.One2many('bim.budget.stage', 'budget_id', 'Stages')
    projection_ids = fields.One2many('bim.budget.stage.projection', 'budget_id', 'Projections')
    space_ids = fields.One2many('bim.budget.space', 'budget_id', 'Spaces')
    asset_ids = fields.One2many('bim.budget.assets', 'budget_id', string='Assets and Discounts')
    concept_count = fields.Integer('Concept N°', compute="_get_concept_count")
    stage_count = fields.Integer('Stages N°', compute="_get_stage_count")
    space_count = fields.Integer('Spaces N°', compute="_get_space_count")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company, readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, copy=True)
    list_price_do = fields.Boolean(compute='_giveme_list_price')
    certification_ids = fields.One2many('bim.massive.certification.by.line','budget_id')
    certification_count = fields.Integer(compute='_compute_certifification_count')
    pvp_id = fields.Many2one('bim.budget.assets', string="A.D.")
    total_main_asset = fields.Float(string="A.D.", related='pvp_id.total')

    def _compute_certifification_count(self):
        for record in self:
            record.certification_count = len(record.certification_ids)

    def action_view_certifications(self):
        certifications = self.mapped('certification_ids')
        action = self.env.ref('base_bim_2.bim_massive_certification_by_line_action').sudo().read()[0]
        if certifications:
            action['domain'] = [('budget_id', '=', self.id)]
            action['context'] = {'default_budget_id': self.id,
                                 'default_project_id': self.project_id.id}
        else:
            action = {
                'type': 'ir.actions.act_window',
                'name': 'New Mass Certification',
                'res_model': 'bim.massive.certification.by.line',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_budget_id': self.id, 'default_project_id': self.project_id.id}
            }
        return action

    def _giveme_list_price(self):
        if self.env.company.type_work == 'pricelist':
            self.list_price_do = True
        else:
            self.list_price_do = False


    pricelist_id = fields.Many2one('product.pricelist', string='Price list',
                                   default=lambda s: s.env['product.pricelist'].search([], limit=1),
                                   check_company=True, domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    date_start = fields.Date('Start Date', required=True, copy=True, default=fields.Date.today)
    date_end = fields.Date('End Date', copy=True, default=fields.Date.today)
    date_from = fields.Date('Scheduled start date', compute='_compute_dates')
    date_to = fields.Date('Scheduled end date', compute='_compute_dates')
    do_compute = fields.Boolean('Calculate', default=True)
    # use_programmed = fields.Boolean('Usar fechas programadas')  # En caso de querer usar el check, pero creo que se debería borrar...
    obs = fields.Text('Notes', copy=True)
    header_notes = fields.Text('Notes', copy=True)
    incidents = fields.Text('Incidences', copy=False)
    order_mode = fields.Selection([
        ('sequence', 'By Sequence'),
        ('code', 'By Codes')],
         'Generate precedents',
         required=True, default='sequence', copy=True)
    type = fields.Selection([
        ('budget', 'Budget'),
        ('certification', 'Certification'),
        ('execution', 'Execution'),
        ('gantt', 'Programming')],
        string='Tipo', default='budget', tracking=True, copy=True)

    state_id = fields.Many2one(
        'bim.budget.state', string='State', index=True, tracking=True,
        compute='_compute_state_id', readonly=False, store=True,
        copy=False, ondelete='restrict', default= lambda s: s.env['bim.budget.state'].search([], limit=1))

    planning_method = fields.Selection([
        ('uniform', 'Uniform distribution'),
        ('dates', 'Gantt planning'),
        ], 'Planning')
    stage_analysis = fields.Many2one('bim.budget.stage', string='Stage', domain="[('state','in',['process','approved']),('budget_id','=',id)]")
    stage_cost_var = fields.Float('Cost Variation (CV)', related='stage_analysis.cost_variation')
    stage_cost_performance= fields.Float('Cost Perform (CPI)', related='stage_analysis.stage_cost_perform')
    stage_advance_var = fields.Float('Advance Variation (SV)', related='stage_analysis.advance_variation')
    stage_advance_performance = fields.Float('Advance Perform (SPI)', related='stage_analysis.stage_advance_perform')
    cost_var_analysis = fields.Text('CV Analysis', readonly=True)
    cost_perf_analysis = fields.Text('CPI Analysis', readonly=True)
    advance_var_analysis = fields.Text('SV Analysis', readonly=True)
    advance_perf_analysis = fields.Text('SPI Analysis', readonly=True)
    summary_cv = fields.Text('CV Summary', readonly=True)
    summary_sv = fields.Text('SV Summary', readonly=True)
    projection_type = fields.Selection([('optimistic', 'Optimistic'),
                                        ('realistic', 'Realistic'),
                                        ('pessimistic', 'Pessimistic')],
                                       string='Projection Type', default='optimistic',
                                       required=True)
    projection_conclusion = fields.Text('Summary VAC', readonly=True)
    projection_decoration = fields.Float(default=0)


    @api.onchange('stage_analysis')
    def update_stage_analysis(self):
        cv_analysis = ''
        sv_analysis = ''
        cpi_analysis = ''
        spi_analysis = ''
        summ_cv = ''
        summ_sv = ''
        if self.stage_analysis:
            if self.stage_cost_var > 0:
                cv_analysis = _('The project is under budget, expenses have been less than expected.\nPossible causes:\n Good price negotiation.\n Cost control.\n Savings due to poor quality of workmanship or materials.\nMeasures:\n Identify the origin of the causes of savings\n Keeping up with the work')
                summ_cv = _('Under budget')
            elif self.stage_cost_var == 0:
                cv_analysis = _('The project is right on budget, expenses have been exactly what was expected.\nMeasures:\n Keeping up with the work')
                summ_cv = _('According to budget')
            elif self.stage_cost_var < 0:
                cv_analysis = _('Project is over budget, expenses have been more than expected.\nPossible causes:\n Productivity did not reach the estimated value\n Setbacks that have created expenses, project changes, rains, strikes, etc.\nMeasures:\n Identify the source of losses\n Take steps to eradicate losses')
                summ_cv = _('Over budget')
            if self.stage_advance_var > 0:
                sv_analysis = _('The project is advanced, it has been executed more than planned in the planning.\nPossible causes:\n Actual productivity exceeded estimate\n Excessively fast and poor quality execution\nMeasures:\n Identify the origin of the causes of savings\n Keeping up with the work')
                summ_sv = _('Project advanced')
            elif self.stage_advance_var == 0:
                sv_analysis = _('The project is on time, exactly what was planned in the planning has been executed.\nMeasures:\n Keeping up with the work')
                summ_sv = _('Project on time')
            elif self.stage_advance_var < 0:
                sv_analysis = _('The project is delayed, less than planned has been executed.\nPossible causes:\n The real productivity did not reach the estimated.\n Setbacks that have delayed work, project changes, rains, strikes, etc.\nMeasures:\n Identify the source of arrears\n Take steps to eradicate arrears')
                summ_sv = _('Project delayed')
            if self.stage_cost_performance > 1:
                cpi_analysis = _('The actual cost is less than the budget, the project is being cheaper')
            elif self.stage_cost_performance == 1:
                cpi_analysis = _('So far the cost has been exactly the amount in the budget')
            elif self.stage_cost_performance < 1:
                cpi_analysis = _('The cost is being more than expected according to the budget')
            if self.stage_advance_performance > 1:
                spi_analysis = _('It has been executed more than expected, the project is advanced')
            elif self.stage_advance_performance == 1:
                spi_analysis = _('Progress is according to plan')
            elif self.stage_advance_performance < 1:
                spi_analysis = _('It has been executed less than expected, the project is behind schedule.')
        self.cost_var_analysis = cv_analysis
        self.advance_var_analysis = sv_analysis
        self.cost_perf_analysis = cpi_analysis
        self.advance_perf_analysis = spi_analysis
        self.summary_cv = summ_cv
        self.summary_sv = summ_sv

    def update_certifications(self):
        for stage in self.stage_ids:
            certif = 0
            fixed = 0
            stages = 0
            measure = 0
            if stage.state == 'process' or stage.state == 'approved':
                self.env.cr.execute("SELECT SUM(amount_certif) AS cert_stage FROM bim_concepts INNER JOIN bim_certification_stage ON bim_concepts.id = bim_certification_stage.concept_id WHERE bim_certification_stage.stage_id = {} AND bim_concepts.type <> 'chapter' AND bim_concepts.budget_id = {}".format(stage.id, self.id))
                if self.env.cr.rowcount:
                    stage_cert = self.env.cr.dictfetchall()
                    temp_stage = stage_cert[0]['cert_stage']
                    if temp_stage:
                        stages = temp_stage
                self.env.cr.execute("SELECT SUM(subtotal) AS subtotal FROM (SELECT bim_concepts.amount_compute_cert as price, bim_concept_measuring.amount_subtotal as amount, bim_concepts.amount_compute_cert * bim_concept_measuring.amount_subtotal as subtotal FROM bim_concepts INNER JOIN bim_concept_measuring ON bim_concepts.id = bim_concept_measuring.concept_id WHERE bim_concept_measuring.stage_id = {} AND bim_concepts.budget_id = {}) INFORM".format(stage.id, self.id))
                if self.env.cr.rowcount:
                    measure_cert = self.env.cr.dictfetchall()
                    temp_measure = measure_cert[0]['subtotal']
                    if temp_measure:
                        measure = temp_measure
                if stage == self.stage_ids[0]:
                    self.env.cr.execute("SELECT sum(balance_cert) AS amount_fixed FROM bim_concepts WHERE type_cert = 'fixed' AND budget_id = {}".format(self.id))
                    if self.env.cr.rowcount:
                        fixed_cert = self.env.cr.dictfetchall()
                        temp_fixed = fixed_cert[0]['amount_fixed']
                        if temp_fixed:
                            fixed = temp_fixed
                        certif = stages + measure + fixed
                    self.stage_ids[0].certification = certif
                else:
                    certif = stages + measure
            stage.certification = certif

    def update_planning(self):
        if self.planning_method == 'uniform':
            for stage in self.stage_ids:
                if self.stage_count > 0:
                    stage.planning = self.balance / self.stage_count
        elif self.planning_method == 'dates':
            for stage in self.stage_ids:
                if not stage.date_start or not stage.date_stop:
                    continue
                start = stage.date_start
                stop = stage.date_stop
                total = 0
                # Estos son los conceptos en la raiz, dentro del periodo de la etapa
                for concept in self.concept_ids:
                    # Me quedo con los conceptos que tengan fecha y que solo sean de la raiz, y que tengan importe
                    if not concept.acs_date_start or not concept.acs_date_end or concept.parent_id or not concept.balance:
                        continue
                    concept_start = concept.acs_date_start.date()
                    concept_stop = concept.acs_date_end.date()
                    # Y ahora solo me quedo con aquellos que sean del periodo
                    if concept_start > stop or concept_stop < start:
                        continue
                    # Calculamos cuanto dura este concepto en días
                    days = (concept_stop - concept_start).days + 1
                    if not days:
                        # Si de casualidad no hay días de diferencia, nos vamos..
                        continue
                    balance_per_day = concept.balance / days
                    stage_start = start if start > concept_start else concept_start
                    stage_stop = stop if stop < concept_stop else concept_stop
                    stage_duration = relativedelta(stage_stop, stage_start).days + 1
                    total += balance_per_day * stage_duration
                stage.planning = total
        else:
            self.stage_ids.write({'planning': 0})

    def update_execution(self):
        vat = self.company_id.include_vat_in_indicators
        first_stage_date = self.stage_ids[0].date_start
        last_stage_date = self.stage_ids[-1].date_stop
        for stage in self.stage_ids:
            opening = 0
            temp_invoice = 0
            temp_refund = 0
            temp_out_mat = 0
            temp_dev_mat = 0
            start_out_mat = 0
            end_out_mat = 0
            start_dev_mat = 0
            end_dev_mat = 0
            start_in_inv = 0
            end_in_inv = 0
            start_in_ref = 0
            end_in_ref = 0
            part = 0
            start_parts = 0
            end_parts = 0
            self.env.cr.execute("SELECT bim_part.date AS check_date, bim_part_line.product_uom_qty * bim_part_line.price_unit AS amount FROM bim_part INNER JOIN bim_part_line ON bim_part.id = bim_part_line.part_id "
                "WHERE bim_part.state IN ('validated') AND bim_part.budget_id = {}".format(self.id))
            if self.env.cr.rowcount:
                temp_part = self.env.cr.dictfetchall()
                for parts in temp_part:
                    if parts['check_date'] < first_stage_date:
                        start_parts += parts['amount']
                    elif parts['check_date'] > last_stage_date:
                        end_parts += parts['amount']
                    elif parts['check_date'] >= stage.date_start and parts['check_date'] < stage.date_stop:
                        part += parts['amount']
            self.env.cr.execute("SELECT attendance_cost as amount, check_in as start FROM hr_attendance WHERE budget_id = {}".format(self.id))
            attendance = 0
            start_attend = 0
            end_attend = 0
            if self.env.cr.rowcount:
                temp_attendance = self.env.cr.dictfetchall()
                for attend in temp_attendance:
                    tmp = attend['start']
                    date_to_compare = date(tmp.year, tmp.month, tmp.day)
                    if date_to_compare < first_stage_date:
                        start_attend += attend['amount']
                    elif date_to_compare > last_stage_date:
                        end_attend += attend['amount']
                    elif date_to_compare >= stage.date_start and date_to_compare < stage.date_stop:
                        attendance += attend['amount']
            self.env.cr.execute("SELECT total_cost AS amount_out, date_done AS date FROM stock_picking INNER JOIN stock_picking_type ON stock_picking.picking_type_id = stock_picking_type.id "
                                "WHERE include_for_bim = True AND bim_budget_id = {} AND state = 'done' AND stock_picking.returned = 'false'".format(self.id))
            if self.env.cr.rowcount:
                amount_store_out = self.env.cr.dictfetchall()
                for amount_out in amount_store_out:
                    tmp = amount_out['date']
                    date_to_compare = date(tmp.year, tmp.month, tmp.day)
                    if date_to_compare < first_stage_date:
                        start_out_mat += amount_out['amount_out']
                    elif date_to_compare > last_stage_date:
                        end_out_mat += amount_out['amount_out']
                    elif date_to_compare >= stage.date_start and date_to_compare < stage.date_stop:
                        temp_out_mat += amount_out['amount_out']
            self.env.cr.execute("SELECT total_cost AS amount_dev, date_done AS date FROM stock_picking INNER JOIN stock_picking_type ON stock_picking.picking_type_id = stock_picking_type.id "
                                "WHERE include_for_bim = True AND bim_budget_id = {} AND state = 'done' AND stock_picking.returned = 'true'".format(self.id))
            if self.env.cr.rowcount:
                amount_store_dev = self.env.cr.dictfetchall()
                for amount_dev in amount_store_dev:
                    tmp = amount_dev['date']
                    date_to_compare = date(tmp.year, tmp.month, tmp.day)
                    if date_to_compare < first_stage_date:
                        start_dev_mat += amount_dev['amount_dev']
                    elif date_to_compare > last_stage_date:
                        end_dev_mat += amount_dev['amount_dev']
                    elif date_to_compare >= stage.date_start and date_to_compare < stage.date_stop:
                        temp_dev_mat += amount_dev['amount_dev']
            store = temp_out_mat - temp_dev_mat
            store_start = start_out_mat - start_dev_mat
            store_end = end_out_mat - end_dev_mat
            self.env.cr.execute("SELECT account_move_line.price_total AS price_total, account_move.invoice_date AS date_inv, account_move_line.price_subtotal AS subtotal FROM account_move_line INNER JOIN account_move "
                                "ON account_move_line.move_id = account_move.id WHERE account_move.state = 'posted' AND account_move_line.budget_id = {} "
                                "AND account_move.move_type = 'in_invoice' AND account_move.include_for_bim = True".format(self.id))
            if self.env.cr.rowcount:
                amount_out_inv = self.env.cr.dictfetchall()
                for amount in amount_out_inv:
                    if vat:
                        temp_amount = amount['price_total']
                    else:
                        temp_amount = amount['subtotal']
                    if amount['date_inv'] < first_stage_date:
                        start_in_inv += temp_amount
                    elif amount['date_inv'] > last_stage_date:
                        end_in_inv += temp_amount
                    elif amount['date_inv'] >= stage.date_start and amount['date_inv'] < stage.date_stop:
                        temp_invoice += temp_amount
            self.env.cr.execute("SELECT account_move_line.price_total AS price_total, account_move.invoice_date AS date_ref, account_move_line.price_subtotal AS subtotal FROM account_move_line INNER JOIN account_move "
                                "ON account_move_line.move_id = account_move.id WHERE account_move.state = 'posted' AND account_move_line.budget_id = {} "
                                "AND account_move.move_type = 'in_refund' AND account_move.include_for_bim = True".format(self.id))
            if self.env.cr.rowcount:
                amount_in_refund = self.env.cr.dictfetchall()
                for amount in amount_in_refund:
                    if vat:
                        temp_amount = amount['price_total']
                    else:
                        temp_amount = amount['subtotal']
                    if amount['date_ref'] < first_stage_date:
                        start_in_ref += temp_amount
                    elif amount['date_ref'] > last_stage_date:
                        end_in_ref += temp_amount
                    elif amount['date_ref'] >= stage.date_start and amount['date_ref'] < stage.date_stop:
                        temp_refund += temp_amount
            invoice = temp_invoice - temp_refund
            invoice_start = start_in_inv - start_in_ref
            invoice_end = end_in_inv - end_in_ref
            if stage == self.stage_ids[0]:
                self.env.cr.execute("SELECT SUM(amount) as opening FROM bim_opening_balance WHERE budget_id = {}".format(self.id))
                if self.env.cr.rowcount:
                    open_amount = self.env.cr.dictfetchall()
                    temp_open = open_amount[0]['opening']
                    if temp_open:
                        opening = temp_open
                    total = part + start_parts + attendance + start_attend + store + store_start + invoice + invoice_start + opening
                    self.stage_ids[0].executed = total
            elif stage == self.stage_ids[-1]:
                total = part + end_parts + attendance + end_attend + store + store_end + invoice + invoice_end
                self.stage_ids[-1].executed = total
            else:
                total = part + attendance + store + invoice
                stage.executed = total

    def update_variations(self):
        cpi = 0
        spi = 0
        sum_EV = 0
        sum_AC = 0
        sum_PV = 0
        for stage in self.stage_ids:
            sum_EV += stage.certification
            sum_AC += stage.executed
            sum_PV += stage.planning
            cv = stage.certification - stage.executed
            sv = stage.certification - stage.planning
            if sum_AC > 0 or sum_AC < 0:
                cpi = sum_EV / sum_AC
            if sum_PV > 0 or sum_PV < 0:
                spi = sum_EV / sum_PV
            stage.stage_cost_perform = cpi
            stage.stage_advance_perform = spi
            stage.cost_variation = cv
            stage.advance_variation = sv

    def compute_budget_updates(self):
        if not self.stage_ids:
            raise UserError(_("This budget has not stages. Please generate them first!"))
        self.update_planning()
        self.update_certifications()
        self.update_execution()
        self.update_variations()
        self.update_budget_graph()
        self.update_projection()

    @api.onchange('projection_type')
    def update_projection(self):
        eac = 0
        vac = 0
        tcpi = 0
        etc = 0
        sum_AC = 0
        sum_EV = 0
        projection = self.env['bim.budget.stage.projection']
        for stage in self.stage_ids:
            sum_AC += stage.executed
            sum_EV += stage.certification
            if self.projection_type == 'optimistic':
                eac = sum_AC + (self.balance - sum_EV)
            elif self.projection_type == 'realistic':
                if stage.stage_cost_perform > 0 or stage.stage_cost_perform < 0:
                    eac = sum_AC + ((self.balance - sum_EV) / stage.stage_cost_perform)
                else:
                    eac = sum_AC
            elif self.projection_type == 'pessimistic':
                if stage.stage_advance_perform == 0 or stage.stage_cost_perform == 0:
                    eac = sum_AC
                else:
                    eac = sum_AC + ((self.balance - sum_EV) / (stage.stage_advance_perform * stage.stage_cost_perform))
            vac = self.balance - eac
            tcpi = (self.balance - sum_EV)/(self.balance - sum_AC) if (self.balance - sum_AC) else 0
            etc = eac - sum_AC
            if stage == self.stage_ids[-1]:
                self.projection_decoration = vac
                if vac > 0:
                    self.projection_conclusion = _('The projected cost is less than the total budget: \nSaving {} €').format(round(vac,2))
                if vac == 0:
                    self.projection_conclusion = _('The expected cost is equal to the budget: \nExact budget')
                if vac < 0:
                    self.projection_conclusion = _('The projected cost is higher than the budget: \nLosses {} €').format(round(vac,2))
            found = False
            for projection_line in self.projection_ids.filtered_domain([('stage_id','=',stage.ids[0])]):
                projection_line.budget_at_end = self.balance
                projection_line.estimate_at_end = eac
                projection_line.estimate_up_to_end = etc
                projection_line.variation_at_end = vac
                projection_line.work_to_be_done = round(tcpi,2)
                found = True
            if not found:
                vals = {
                    'budget_id': self.id,
                    'stage_id': stage.ids[0],
                    'budget_at_end': self.balance,
                    'estimate_at_end': eac,
                    'estimate_up_to_end': etc,
                    'variation_at_end': vac,
                    'work_to_be_done': round(tcpi,2),
                }
                projection.create(vals)

    def update_budget_graph(self):
        if not plt:
            return

        field_monetary = self.env['ir.qweb.field.monetary']

        @ticker.FuncFormatter
        def format_monetary(amount, pos):
            value = field_monetary.value_to_html(amount, {'display_currency': self.currency_id})
            value = re.sub('<[^<]+?>', '', value)
            return value

        for record in self:
            stages = []
            cert_vals = []
            exc_vals = []
            pln_vals = []
            cert_count = exc_count = pln_count = 0
            for stage in record.stage_ids:
                stages.append(stage.name)
                cert_vals.append(stage.certification + cert_count)
                exc_vals.append(stage.executed + exc_count)
                pln_vals.append(stage.planning + pln_count)
                cert_count += stage.certification
                exc_count += stage.executed
                pln_count += stage.planning
            fig = plt.figure(figsize=(15,5))
            ax = fig.add_subplot(111)
            ax.yaxis.set_major_formatter(format_monetary)
            ax.plot(stages, pln_vals, color='blue', marker='.', label=_('Planned'))
            ax.plot(stages, cert_vals, color='green', marker='.', label=_('Certified'))
            ax.plot(stages, exc_vals, color='red', marker='.', label=_('Real'))
            plt.title(_('Budget analysis'), fontsize=14)
            plt.legend(loc='lower center', ncol=len(stages), bbox_to_anchor=(0.5, -0.2))
            plt.grid(True)
            figfile = io.BytesIO()
            plt.savefig(figfile, format='png', bbox_inches='tight', pad_inches=0)
            plt.clf()
            plt.cla()
            plt.close()
            figfile.seek(0)
            record.analysis_graph = base64.b64encode(figfile.getvalue())

    def _compute_state_id(self):
        state_obj = self.env['bim.budget.state']
        for budget in self:
            if not budget.state_id:
                budget.state_id = state_obj.search([('is_new', '=', True)], limit=1).id

    gantt_type = fields.Selection([('begin', 'Calculated Start'),
                                   ('end', 'Calculated End'),
                                   ('time', 'Calculated Duration')], 'Programming', default='end', required=True)
    detailed_retification_ids = fields.One2many('bim.product.rectify.detailed', 'budget_id', readonly=False)

    amount_total_equip = fields.Monetary('Total equipment', compute="_get_amount_total")
    amount_total_labor = fields.Monetary('Total labor', compute="_get_amount_total")
    amount_total_material = fields.Monetary('Total material', compute="_get_amount_total")
    amount_total_other = fields.Monetary('Total others', compute="_get_amount_total")

    amount_certified_equip = fields.Monetary('Certified equipment', compute="_get_amount_total")
    amount_certified_labor = fields.Monetary('Certified labor', compute="_get_amount_total")
    amount_certified_material = fields.Monetary('Certified material', compute="_get_amount_total")
    amount_certified_other = fields.Monetary('Certified other', compute="_get_amount_total")

    amount_executed_equip = fields.Monetary('Executed equipment', compute="_compute_execute")
    amount_executed_labor = fields.Monetary('Executed labor', compute="_compute_execute")
    amount_executed_material = fields.Monetary('Executed material', compute="_compute_execute")
    amount_executed_other = fields.Monetary('Executed other', compute="_compute_execute")
    product_rectify_ids = fields.One2many('bim.product.rectify', 'budget_id', 'Product rectifications')
    balance_certified_residual = fields.Float(string='To invoice', compute='compute_balance_certified_residual', store=True)
    certification_factor = fields.Float(compute='compute_certification_factor', store=True)
    cost_list_id = fields.Many2one('bim.cost.list')
    use_cost_list = fields.Boolean(compute='_giveme_cost_list')
    bim_certificate_chapters = fields.Boolean(compute='_compute_bim_certificate_chapters')
    chapter_certification_ids = fields.One2many('bim.massive.chapter.certification', 'budget_id')
    chapter_certification_count = fields.Integer(compute='_compute_chapter_certification_count')
    limit_certification = fields.Boolean(default=lambda self: self.env.company.limit_certification)
    limit_certification_percent = fields.Integer(default=lambda self: self.env.company.limit_certification_percent)

    def _compute_chapter_certification_count(self):
        for record in self:
            record.chapter_certification_count = len(record.chapter_certification_ids)

    def _compute_bim_certificate_chapters(self):
        self.bim_certificate_chapters = self.company_id.bim_certificate_chapters

    def _giveme_cost_list(self):
        if self.env.company.type_work == 'costlist':
            self.use_cost_list = True
        else:
            self.use_cost_list = False

    def action_view_chapter_certifications(self):
        certifications = self.mapped('chapter_certification_ids')
        action = self.env.ref('base_bim_2.bim_massive_chapter_certification_action').sudo().read()[0]
        if certifications:
            action['domain'] = [('budget_id', '=', self.id)]
            action['context'] = {'default_budget_id': self.id,
                                 'default_project_id': self.project_id.id}
        else:
            action = {
                'type': 'ir.actions.act_window',
                'name': 'New Mass Certification',
                'res_model': 'bim.massive.chapter.certification',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_budget_id': self.id, 'default_project_id': self.project_id.id}
            }
        return action

    @api.depends('asset_ids.total','balance')
    def compute_certification_factor(self):
        for record in self:
            record.compute_indicators()
            certification_factor = 1
            if record.asset_ids:
                total = 0
                for asset in record.asset_ids:
                    total = asset.total
                for asset in record.asset_ids:
                    if asset.asset_id.type == 'O' and asset.asset_id.not_billable:
                        total -= asset.total
                if total > 0 and record.balance > 0:
                    certification_factor = total /record.balance
            record.certification_factor = certification_factor

    @api.depends('concept_ids.balance_cert')
    def compute_balance_certified_residual(self):
        for record in self:
            record._compute_amount()
            amount = 0
            cancel = 0
            in_payment_state = self.env['bim.paidstate.line'].search([('budget_id', '=', record.id), ('is_loaded', '=', True)])
            for paidstate in in_payment_state:
                amount += paidstate.amount
                if paidstate.paidstate_id.state == 'cancel':
                    cancel += paidstate.amount
            record.balance_certified_residual = record.certified - amount + cancel

    def print_budget_notes(self):
        return self.env.ref('base_bim_2.notes_report_budget').report_action(self)

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            self.currency_id = self.project_id.currency_id.id
            if self.project_id.customer_id.property_product_pricelist:
                self.pricelist_id = self.project_id.customer_id.property_product_pricelist.id

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            self.pvp_id = False
            self.asset_ids = [(5,)]
            self._create_assets(self.template_id)
        else:
            self.pvp_id = False
            self.asset_ids = [(5,)]

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id.user_ids and self.env.user.id not in self.state_id.user_ids.ids:
            users = ""
            for user in self.state_id.user_ids:
                users += user.display_name + ", "
            raise UserError(
                _("Only users {} can set current Budget to state {}").format(users[:-2], self.state_id.name))

    @api.depends('concept_ids')
    def _compute_dates(self):
        today = fields.Datetime.today()
        for record in self:
            record.date_from = min([c.acs_date_start for c in record.concept_ids if c.acs_date_start], default=record.date_start or today)
            record.date_to = max([c.acs_date_end for c in record.concept_ids if c.acs_date_end], default=record.date_end or today)

    def set_estimated_dates(self):
        for record in self:
            record.date_start = record.date_from
            record.date_end = record.date_to

    def action_budget_send(self):
        self.ensure_one()
        wizard = self.env['bim.budget.report.wizard']
        wizard = wizard.create({
                'display_type': 'full',
                'summary_type': 'departure',
                'total_type': 'normal',
                'filter_type': 'space',
                'budget_id': self.id,
                'project_id': self.project_id.id,
                'text': True,
                'filter_ok': False,
        })
        pdf = self.env.ref('base_bim_2.bim_budget_full')._render_qweb_pdf(wizard.id)
        b64_pdf = base64.b64encode(pdf[0])
        ATTACHMENT_NAME = self.name
        attach_report = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })
        template_id = self.env['ir.model.data'].xmlid_to_res_id('base_bim_2.email_template_budget', raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        template.attachment_ids = [(6,0,[attach_report.id])]
        if template.lang:
            lang = template._render_template(template.lang, 'bim.budget', self.ids)
        ctx = {
            'default_model': 'bim.budget',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            #'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_view_concepts(self):
        concepts = self.mapped('concept_ids')
        action = self.env.ref('base_bim_2.action_bim_concepts').sudo().read()[0]
        if concepts:
            action['domain'] = [('budget_id', '=', self.id)]#('parent_id', '=', False),
            action['context'] = {'default_budget_id': self.id}
        else:
            action = {
                'type': 'ir.actions.act_window',
                'name': 'New Concept',
                'res_model': 'bim.concepts',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_budget_id': self.id, 'default_type': 'chapter'}
            }
        action['context'].update({'budget_type': self.type})
        return action

    def action_view_stages(self):
        stages = self.mapped('stage_ids')
        action = self.env.ref('base_bim_2.action_bim_budget_stage').sudo().read()[0]
        if len(stages) > 0:
            action['domain'] = [('id', 'in', stages.ids),('budget_id', '=', self.id)]
            action['context'] = {'default_budget_id': self.id}
        else:
            action = {
                'type': 'ir.actions.act_window',
                'name': 'New Stage',
                'res_model': 'bim.budget.stage',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_budget_id': self.id}
            }
        return action

    def action_view_spaces(self):
        spaces = self.mapped('space_ids')
        action = self.env.ref('base_bim_2.action_bim_budget_space').sudo().read()[0]
        if len(spaces) > 0:
            action['domain'] = [('id', 'in', spaces.ids),('budget_id', '=', self.id)]
            action['context'] = {'default_budget_id': self.id}
        else:
            action = {
                'type': 'ir.actions.act_window',
                'name': 'New',
                'res_model': 'bim.budget.space',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_budget_id': self.id}
            }
        return action

    def print_certification(self):
        return self.env.ref('base_bim_2.bim_budget_certification').report_action(self)

    def name_get(self):
        reads = self.read(['name', 'code'])
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = "[" + record['code'] + '] ' + name
            res.append((record['id'], name))
        return res

    def _create_assets(self,template):
        assets = []
        assets_obj = self.env['bim.budget.assets']
        for tmpl_line in template.line_ids:
            vals = {'budget_id':self.id,'asset_id':tmpl_line.asset_id.id,'value':tmpl_line.value,'sequence':tmpl_line.sequence, 'main_asset': tmpl_line.main_asset}
            asset_line = assets_obj.create(vals)
            assets.append(asset_line.id)

            # Actualizamos los afectos
            if tmpl_line.affect_ids:
                af_ids = [af.asset_id.id for af in tmpl_line.affect_ids]
                line_ids =[l.id for l in self.asset_ids if l.asset_id.id in af_ids]
                asset_line.affect_ids = [(6,0,line_ids)]
        for asset in self.asset_ids.filtered_domain([('main_asset','=',True)]):
            self.pvp_id = asset.id
            break
        return True

    def compute_indicators(self):
        list_vals = ['M','Q','H','S']
        indicator_obj = self.env['bim.budget.indicator']
        for budget in self:
            if not budget.indicator_ids:
                for type in list_vals:
                    indicator_obj.create({'budget_id': budget.id,'type': type})

    def update_amount(self):
        for budget in self:
            last_level = budget.concept_ids.filtered(lambda r: r.type in ['departure','labor','equip','material','aux'])

            for res in last_level:
                res.update_amount()

            for res in last_level:
                parent = res.parent_id
                while parent:
                    parent.update_amount()
                    if parent.parent_id:
                        parent = parent.parent_id
                    else:
                        parent = False
            budget.update_assets_total()

    def update_assets_total(self):
        for budget in self:
            for asset in budget.asset_ids:
                asset._compute_total()

    def incident_review(self):
        for budget in self:
            incidents = []
            chapters = budget.concept_ids.filtered(lambda r: r.type in ['chapter'])
            resources = budget.concept_ids.filtered(lambda r: r.type in ['labor','equip','material'])
            for res in resources:
                if not res.product_id:
                    incidents.append(inconsistency['1']%res.display_name)
                if res.child_ids:
                    incidents.append(inconsistency['9']%res.display_name)
                if res.balance == 0:
                    incidents.append(inconsistency['7']%res.display_name)
                if res.type == 'labor' and res.product_id and res.product_id.resource_type != 'H':
                    incidents.append(inconsistency['4']%(res.product_id.display_name,res.display_name))
                if res.type == 'equip' and res.product_id and res.product_id.resource_type != 'Q':
                    incidents.append(inconsistency['3']%(res.product_id.display_name,res.display_name))
                if res.type == 'material' and res.product_id and res.product_id.resource_type != 'M':
                    incidents.append(inconsistency['2']%(res.product_id.display_name,res.display_name))
                if res.type == 'material' and res.product_id and res.product_id.type == 'service':
                    incidents.append(inconsistency['5']%(res.product_id.display_name,res.display_name))
                if res.type == 'labor' and res.product_id and res.product_id.type == 'product':
                    incidents.append(inconsistency['6']%(res.product_id.display_name,res.display_name))
                if res.uom_id and res.product_id and res.uom_id != res.product_id.uom_id:
                    incidents.append(inconsistency['10']%(res.display_name,res.product_id.display_name,res.parent_id.display_name))

            for cap in chapters:
                if cap.quantity > 1:
                    incidents.append(inconsistency['8']%(cap.display_name))

            if not incidents:
                incidents.append(inconsistency['0'])
            budget.incidents = '\n'.join(incidents)

    def create_stage(self, interval=1): #3 Trimestral, 2 Bimensual, 6 Semestral
        stage_obj = self.env['bim.budget.stage']
        for budget in self:
            bstart = budget.date_start
            bend = budget.date_end
            if not bend:
                raise UserError(_('To create the stages you must enter an end date'))
            if bend <= bstart:
                raise UserError(_('To create the stages, you must enter an End date greater than the Start date'))

            stage = 1
            while bstart < bend:
                if interval == 15:
                    next_date = bstart + relativedelta(days=interval)
                    next_date = next_date - relativedelta(days=1)
                else:
                    next_date = bstart + relativedelta(months=interval, days=-1)

                if next_date > bend:
                    next_date = bend

                stage_obj.create({
                    'name': _("Stage %s") % str(stage),
                    'code': str(stage),#.zfill(3)
                    'date_start': bstart,
                    'date_stop':  next_date,
                    'budget_id': budget.id,
                    'state': 'process' if stage == 1 else 'draft',
                })
                stage += 1
                if interval == 15:
                    bstart = bstart + relativedelta(days=interval)
                else:
                    bstart = bstart + relativedelta(months=interval)
        return True

    def create_measures(self, measure_ids, concept):
        meobj = self.env['bim.concept.measuring']
        for record in measure_ids:
            data_me = record.copy_data()[0]
            data_me['space_id'] = False #vacios ya que se generan luego
            data_me['concept_id'] = concept.id
            meobj.create(data_me)

    def recursive_create(self, child_ids, budget, parent, cobj):
        for record in child_ids:
            data_rec = record.copy_data()[0]
            data_rec['budget_id'] = budget.id
            data_rec['parent_id'] = parent.id
            next_level = cobj.create(data_rec)
            if record.measuring_ids:
                self.create_measures(record.measuring_ids,next_level)
            if record.child_ids:
                self.recursive_create(record.child_ids, budget, next_level, cobj)

    def rectify_products(self):
        def get_origin_name(concept):
            if not concept.parent_id:
                return concept.display_name.replace(";", ".")
            return get_origin_name(concept.parent_id) + ' - ' + concept.display_name.replace(";", ".")

        # if not self.env.user.has_group('base_bim_2.group_rectify_products'):
        #     raise ValidationError(_('You do not have permissions to rectify products.'))

        types = dict(self.env['bim.concepts']._fields['type'].selection)
        products_by_code = {}
        product_obj = self.env['product.product']
        changes = []
        not_created = []
        not_changed = []
        for concept in self.concept_ids:
            if concept.type in ['chapter', 'departure']:
                continue
            if not concept.product_id or not concept.code:
                not_changed.append((get_origin_name(concept), types.get(concept.type, ''), concept.product_id.default_code or '', '', concept.uom_id.name or '', ''))
                continue
            if concept.code != concept.product_id.default_code:
                product = products_by_code.get(concept.code)
                if not product:
                    product = product_obj.search([('default_code', '=', concept.code)], limit=1)
                    if product:
                        products_by_code[concept.code] = product
                if product:
                    changes.append((get_origin_name(concept), types.get(concept.type, ''), concept.product_id.default_code or '', product.default_code or '', concept.uom_id.name or '', product.uom_id.name or ''))
                    concept.product_id = product
                else:
                    not_created.append(concept.display_name)
                    not_changed.append((get_origin_name(concept), types.get(concept.type, ''), concept.product_id.default_code or '', product.default_code or '', concept.uom_id.name or '', product.uom_id.name or ''))
        if not changes and not_created:
            raise ValidationError(_('The following concepts were not rectified because the product does not exist:\n%s' % '\n'.join(not_created)))
        elif not changes:
            raise ValidationError(_('There are no products to rectify'))

        workbook = xlwt.Workbook()
        head = xlwt.easyxf('align: wrap yes, horiz center; font: bold on;')
        head2 = xlwt.easyxf('align: wrap no; font: bold on;')
        sheet = workbook.add_sheet('Rectifications')
        # header
        sheet.write_merge(0, 0, 0, 5, 'Rectifications {self.display_name}', head)
        sheet.write(1, 0, 'Resource', head2)
        sheet.write(1, 1, 'Budget Concept', head2)
        sheet.write(1, 2, 'BIM Code', head2)
        sheet.write(1, 3, 'Code to be replaced', head2)
        sheet.write(1, 4, 'Unit in budget', head2)
        sheet.write(1, 5, 'Unit in product', head2)
        for i, line in enumerate(changes, 2):
            for j, data in enumerate(line):
                sheet.write(i, j, data)
        for i, line in enumerate(not_changed, len(changes) + 2):
            for j, data in enumerate(line):
                sheet.write(i, j, data)

        stream = io.BytesIO()
        workbook.save(stream)
        stream.seek(0)

        now = fields.Datetime.now()
        self.product_rectify_ids.create({
            'budget_id': self.id,
            'csv_file': base64.b64encode(stream.getvalue()),
            'filename': 'Rectifications {now.strftime("%d-%m-%y %H:%M")} por {self.env.user.display_name}.xls',
        })
        return True

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        cobj = self.env['bim.concepts']
        sobj = self.env['bim.budget.space']
        default = dict(default or {})
        default.update(
            code = "New",
            name =_("%s (copy)") % (self.name or ''),
            do_compute=True
        )
        new_copy = super(BimBudget, self).copy(default)

        #Carga de Concepts
        for cap in self.concept_ids.filtered(lambda b: not b.parent_id):
            data_cap = cap.copy_data()[0]
            data_cap['budget_id'] = new_copy.id
            new_cap = cobj.create(data_cap)
            if cap.child_ids:
                self.recursive_create(cap.child_ids,new_copy,new_cap,cobj)

        #Generacion de Haberes y descuentos
        new_copy._create_assets(new_copy.template_id)

        #Generacion de Indicadores
        if self.indicator_ids:
            new_copy.compute_indicators()

        #Generacion de Etapas
        if self.stage_ids:
            new_copy.create_stage()

        # completar Spaces
        if self.space_ids:
            new_copy.space_ids = [(5,)]
            for space in self.space_ids:
                data_space = space.copy_data()[0]
                data_space['budget_id'] = new_copy.id
                sobj.create(data_space)

        # Asociar Spaces en mediciones
        space_obj = self.env['bim.budget.space']
        departures = new_copy.concept_ids.filtered(lambda x:x.type == 'departure')
        for dep in departures:
            for m in dep.measuring_ids:
                if not m.space_id:
                    space = space_obj.search([('budget_id','=',new_copy.id),('name','=',m.name)],limit=1)
                    m.space_id = space and space.id or False

        return new_copy

    def unlink(self):
        for record in self:
            if record.type == 'certification':
                raise ValidationError(_('You cannot delete budgets in certification.'))
        self.concept_ids.filtered(lambda c: not c.parent_id).unlink()
        return super().unlink()

    def import_gantt(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gantt Import',
            'res_model': 'bim.gantt.import',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_budget_id': self.id},
        }

    def export_gantt(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gantt Export',
            'res_model': 'bim.gantt.export',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_budget_id': self.id},
        }

    def import_bim_file(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('BIM File Import'),
            'res_model': 'bim.file.import',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_budget_id': self.id},
        }

    def concept_quantiy_to_cero(self):
        for record in self:
            for concept in record.concept_ids:
                if concept.type == 'departure':
                    concept.quantity = 0
                    for measure in concept.measuring_ids:
                        measure.unlink()
            record.message_post(
                body=_("Amounts in Items Zeroed and Measurements Eliminated by:  %s") % record.env.user.name)

    def load_product_budget_details(self):
        # if not self.env.user.has_group('base_bim_2.group_rectify_products'):
        #     raise ValidationError(_('You are not allow to rectify products.'))

        for line in self.detailed_retification_ids:
            line.unlink()

        product_obj = self.env['product.product']
        detail_rect_obj = self.env['bim.product.rectify.detailed']
        different_product_codes = []
        tmp_list = []
        same_product_codes = []
        for concept in self.concept_ids.filtered(lambda c: c.type in ['labor','equip', 'material']):
            tuple = concept.code + concept.name
            if tuple not in tmp_list:
                if concept.code == concept.product_id.default_code:
                    tmp_list.append(tuple)
                    same_product_codes.append([concept.type,concept.product_id])
                else:
                    tmp_list.append(tuple)
                    product = product_obj.search([('default_code','=',concept.code)])
                    if product:
                        product_id = product
                    else:
                        product_id = concept.product_id
                    different_product_codes.append([concept.type, concept.code, concept.name,product_id])

        for tuple in different_product_codes:
            type = 'M'
            if tuple[0] == 'labor':
                type = 'H'
            elif tuple[0] == 'equip':
                type = 'Q'
            detail_rect_obj.create({
                'budget_id': self.id,
                'type': type,
                'bim_product_code': tuple[1],
                'bim_product_name': tuple[2],
                'odoo_product_id': tuple[3].id
            })

        for tuple in same_product_codes:
            type = 'M'
            if tuple[0] == 'labor':
                type = 'H'
            elif tuple[0] == 'equip':
                type = 'Q'
            detail_rect_obj.create({
                'budget_id': self.id,
                'type': type,
                'bim_product_code': tuple[1].default_code,
                'bim_product_name': tuple[1].name,
                'odoo_product_id': tuple[1].id
            })
        self.rectify_products_from_details()

        return True

    def rectify_products_from_details(self):
        for record in self:
            for line in record.detailed_retification_ids:
                concepts = record.concept_ids.filtered(lambda c: c.type in ['labor','equip', 'material'] and c.code == line.bim_product_code)
                for concept in concepts:
                    concept.product_id = line.odoo_product_id.id


class BimBudgetStage(models.Model):
    _name = 'bim.budget.stage'
    _description = "Budget Stages"
    _order = 'date_start asc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    def action_start(self):
        no_do = False
        for line in self.budget_id.stage_ids.filtered_domain([('id','!=',self.id)]):
            if line.state == 'process':
                no_do = True
        if no_do:
            raise UserError(_('There is a stage in Current state that you have to Approve.'))
        self.write({'state':'process'})
        return self.update_concept()

    def action_approve(self):
        self.write({'state': 'approved'})
        pending = self.search([('state','=','draft'),('budget_id','=',self.budget_id.id)])
        list_date = [line.date_start for line in pending.filtered_domain([('date_start','!=',False)])]
        min_date = list_date and min(list_date) or False
        if min_date:
            value = self.search([('state','=','draft'),('date_start','=',min_date),('budget_id','=',self.budget_id.id)])
            value.action_start()

        return self.update_concept()

    def action_cancel(self):
        self.write({'state':'cancel'})
        return self.update_concept()

    def action_draft(self):
        self.write({'state':'draft'})
        return self.update_concept()

    def name_get(self):
        result = []
        for stage in self:
            if stage.state == 'draft':
                state = _('Pending')
            elif stage.state == 'process':
                state = _('Current')
            elif stage.state == 'approved':
                state = _('Approved')
            else:
                state = _('Cancelled')
            name = stage.name + ' - ' + state
            result.append((stage.id, name))
        return result

    name = fields.Char("Name")
    code = fields.Char("Code")
    date_start = fields.Date('Start Date', copy=False)
    date_stop = fields.Date('End Date', required=True, copy=False)
    budget_id = fields.Many2one('bim.budget', "Budget", ondelete='cascade')
    project_id = fields.Many2one('bim.project', related='budget_id.project_id')
    state = fields.Selection([
        ('draft', 'Pending'),
        ('process', 'Current'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')],
        string='Status', default='draft', copy=False, tracking=True)
    taken = fields.Boolean(default=False)
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True, default=lambda self: self.env.user)
    certification = fields.Float('Certification (EV)', readonly=True, store=True)
    executed = fields.Float('Real Cost (AC)', readonly=True, store=True)
    planning = fields.Float('Planning (PV)', readonly=True, store=True)
    cost_variation = fields.Float('Cost Variation (CV)', readonly=True, store=True)
    advance_variation = fields.Float('Advance Variation (SV)', readonly=True, store=True)
    stage_cost_perform = fields.Float('Cost Perform (CPI)', readonly=True, store=True)
    stage_advance_perform = fields.Float('Advance Perform (SPI)', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', related="budget_id.currency_id")
    projection_stage_ids = fields.One2many('bim.budget.stage.projection', 'stage_id', 'Projections')


    def update_concept(self):
        ''' Este metodo ACTUALIZA los Concepts que esten certificados
        (((Por Medicion o Por etapas))), ajustando los valores segun el
        cambio de state de la Etapa relacionada'''
        concepts = self.budget_id.concept_ids
        stage_concepts = concepts.filtered(lambda c: c.type_cert == 'stage')
        measure_concepts = concepts.filtered(lambda c: c.type_cert == 'measure')

        if stage_concepts:
            for concept in stage_concepts:
                concept._compute_stage()
                concept.onchange_stage()
                concept.onchange_qty_certification()

        if measure_concepts:
            for concept in measure_concepts:
                concept._compute_measure()
                concept.onchange_qty()
                concept.onchange_qty_certification()
        return True

    @api.model
    def create(self, vals):
        res = super(BimBudgetStage, self).create(vals)
        if not res.date_start:
            affected_stage = res.search([('budget_id','=',res.budget_id.id),('id','!=',res.id),('date_stop','>=',res.date_stop),('date_start','<=',res.date_stop)],limit=1)
            if affected_stage:
                res.date_start = affected_stage.date_start
                affected_stage.date_start = res.date_stop + timedelta(days=1)
        for concept in res.budget_id.concept_ids.filtered_domain([('type_cert','=','stage')]):
            concept.update_stage_list(res)
        self.env['bim.budget.stage.projection'].create({
            'budget_id': res.budget_id.id,
            'stage_id': res.id
        })
        return res

    def unlink(self):
        for record in self:
            if record.state == 'approved':
                raise UserError(_("It is not possible to delete an Approved Stage"))
            for concept in record.budget_id.concept_ids:
                if concept.type == "departure":
                    if concept.type_cert == 'stage' and concept.quantity_cert > 0:
                        raise UserError(_("It is not possible to delete and Stage with Certified Quantities"))
        return super().unlink()

    @api.onchange('date_stop')
    def onchange_date_stop(self):
        if self.date_stop and self.budget_id and (self.date_stop < self.budget_id.date_start or self.date_stop > self.budget_id.date_end):
            raise UserError(_("It is not possible to create Stage with Date out of Budget Dates Range from {} to {}").format(self.budget_id.date_start, self.budget_id.date_end))


class BimBudgetSpace(models.Model):
    _name = 'bim.budget.space'
    _description = "Budget Spaces"
    _order = 'id asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_code(self):
        budget_id = self._context.get('default_budget_id')
        budget = self.env['bim.budget'].browse(budget_id)
        return 'S'+str(len(budget.space_ids)+1)

    name = fields.Char("Name")
    code = fields.Char("Code", default=_get_code)
    budget_id = fields.Many2one('bim.budget', "Budget", ondelete="cascade")
    object_id = fields.Many2one('bim.object', "Object")
    project_id = fields.Many2one('bim.project', "Project",related='budget_id.project_id')
    note = fields.Text('Summary')
    purchase_req_ids = fields.One2many('bim.purchase.requisition', 'space_id', 'Materials Request')
    purchase_req_count = fields.Integer('Request N°', compute="_compute_purchase_req_count")

    @api.depends('purchase_req_ids')
    def _compute_purchase_req_count(self):
        for space in self:
            space.purchase_req_count = len(space.purchase_req_ids)

    def action_view_purchase_requisition(self):
        purchases = self.mapped('purchase_req_ids')
        action = self.env.ref('base_bim_2.action_bim_purchase_requisition').sudo().read()[0]
        if len(purchases) > 0:
            action['domain'] = [('id', 'in', purchases.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def name_get(self):
        reads = self.read(['name', 'code'])
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = "[" + record['code'] + '] ' + name
            res.append((record['id'], name))
        return res


class BimBudgetAssets(models.Model):
    _name = 'bim.budget.assets'
    _description = 'Credit or budget discount'
    _rec_name = 'asset_id'
    _order = 'sequence'

    sequence = fields.Integer('Sequence')
    asset_id = fields.Many2one('bim.assets', "Credit or Discount", ondelete='cascade')
    value = fields.Float('Valor', digits=(16,6))
    budget_id = fields.Many2one('bim.budget', "Budget", ondelete='cascade')
    currency_id = fields.Many2one('res.currency', 'Currency', related="budget_id.currency_id")
    total = fields.Float(compute='_compute_total', store=True)
    to_invoice = fields.Boolean('To Invoice', default=True)
    affect_ids = fields.Many2many(
        string='Affects',
        comodel_name='bim.budget.assets',
        relation='budget_assets_afect_rel',
        column1='parent_id',
        column2='child_id',
    )
    main_asset = fields.Boolean()

    @api.depends('value', 'asset_id', 'affect_ids','budget_id.amount_total_material','budget_id.amount_total_labor',
                 'budget_id.amount_total_equip','budget_id.amount_total_other')
    def _compute_total(self):
        amounts = {budget: 0 for budget in self.budget_id}
        amounts[self.budget_id.browse()] = 0
        for record in self:
            budget = record.budget_id
            if record.asset_id.type == 'M':
                value = budget.amount_total_material
            elif record.asset_id.type == 'H':
                value = budget.amount_total_labor
            elif record.asset_id.type == 'Q':
                value = budget.amount_total_equip
            elif record.asset_id.type == 'S':
                value = budget.amount_total_other
            elif record.asset_id.type == 'T':
                value = budget.balance
            elif record.asset_id.type == 'N':
                value = amounts[budget]
            elif record.asset_id.type == 'O':
                value = record.value
            else:
                value = 0.0

            if record.affect_ids:
                total_af = sum(af.total for af in record.affect_ids)
                value = total_af * (record.value / 100)
            if record.asset_id.type in ['O','T']:
                amounts[budget] += value
            record.total = value


class BimBudgetIndicator(models.Model):
    _description = "Comparative indicators"
    _name = 'bim.budget.indicator'

    @api.depends('amount_projected', 'amount_budget')
    def _compute_percent(self):
        for record in self:
            record.percent = record.amount_budget > 0.0 and (record.amount_projected / record.amount_budget) or 0.0


    budget_id = fields.Many2one('bim.budget', 'Budget', ondelete="cascade")
    currency_id = fields.Many2one('res.currency', 'Currency', related="budget_id.currency_id")
    amount_budget = fields.Monetary('Budget', help="Budgeted Value", compute="_compute_total")
    amount_executed = fields.Monetary('Real Executed', help="Warehouse Outlets + Parts", compute="_compute_total")
    amount_projected = fields.Monetary('Actual Projected', help="Difference between the Budget and the Real executed", compute="_compute_total")
    amount_certified = fields.Monetary('Certified', help="Certified value", compute="_compute_total")
    amount_proj_cert = fields.Float('Certified Projected', help="Difference between Budget and Certificate", compute="_compute_total")
    percent = fields.Float('Percentage', help="Percentage given by the real value between the estimated value", compute="_compute_percent")
    type = fields.Selection(
        [('M', 'Materials Cost'),
         ('Q', 'Equipment Cost'),
         ('H', 'Labor Cost'),
         ('S', 'Other Cost') ],
        'Indicator Type', readonly=True)

    @api.depends('budget_id', 'type')
    def _compute_total(self):
        amount = 0
        for record in self:
            budget = record.budget_id
            if record.type == 'M':
                diff_proj_cert = budget.amount_total_material - budget.amount_certified_material
                record.amount_budget = budget.amount_total_material
                record.amount_certified = budget.amount_certified_material + diff_proj_cert if (diff_proj_cert > 0.0 and diff_proj_cert <=  1.0) else budget.amount_certified_material
                record.amount_proj_cert = 0.0 if (diff_proj_cert > 0.0 and diff_proj_cert <=  1.0) else diff_proj_cert
                record.amount_executed = budget.amount_executed_material
                record.amount_projected = budget.amount_total_material - budget.amount_executed_material
            elif record.type == 'H':
                diff_proj_cert = budget.amount_total_labor - budget.amount_certified_labor
                record.amount_budget = budget.amount_total_labor
                record.amount_certified = budget.amount_certified_labor + diff_proj_cert if (diff_proj_cert > 0.0 and diff_proj_cert <=  1.0) else budget.amount_certified_labor
                record.amount_proj_cert = 0.0 if (diff_proj_cert > 0.0 and diff_proj_cert <=  1.0) else diff_proj_cert
                record.amount_executed = budget.amount_executed_labor
                record.amount_projected = budget.amount_total_labor - budget.amount_executed_labor
            elif record.type == 'Q':
                diff_proj_cert = budget.amount_total_equip - budget.amount_certified_equip
                record.amount_budget = budget.amount_total_equip
                record.amount_certified = budget.amount_certified_equip + diff_proj_cert if (diff_proj_cert > 0.0 and diff_proj_cert <=  1.0) else budget.amount_certified_equip
                record.amount_proj_cert = 0.0 if (diff_proj_cert > 0.0 and diff_proj_cert <=  1.0) else diff_proj_cert
                record.amount_executed = budget.amount_executed_equip
                record.amount_projected = budget.amount_total_equip - budget.amount_executed_equip
            elif record.type == 'S':
                diff_proj_cert = budget.amount_total_other - budget.amount_certified_other
                record.amount_budget = budget.amount_total_other
                record.amount_certified = budget.amount_certified_other  + diff_proj_cert if (diff_proj_cert > 0.0 and diff_proj_cert <=  1.0) else budget.amount_certified_other
                record.amount_proj_cert = 0.0 if (diff_proj_cert > 0.0 and diff_proj_cert <=  1.0) else diff_proj_cert
                record.amount_executed = budget.amount_executed_other
                record.amount_projected = budget.amount_total_other - budget.amount_executed_other
            else:
                record.amount_budget = 0
                record.amount_certified = 0
                record.amount_proj_cert = 0
                record.amount_executed = 0
                record.amount_projected = 0

class BimProductRectify(models.Model):
    _name = 'bim.product.rectify'
    _description = 'Rectification of products in budget'
    _order = 'id desc'
    _rec_name = 'filename'

    budget_id = fields.Many2one('bim.budget', 'Bugdet', ondelete='cascade')
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    date = fields.Datetime('Date', default=fields.Datetime.now)
    csv_file = fields.Binary('File', required=True)
    filename = fields.Char('File Name')

class BimProductRectifyDetailed(models.Model):
    _name = 'bim.product.rectify.detailed'
    _description = 'Detailed product rectification'

    budget_id = fields.Many2one('bim.budget', readonly=True)
    bim_product_code = fields.Char(string='BIM Code', required=True, readonly=True)
    type = fields.Selection([
        ('H', 'LABOR'),
        ('Q', 'EQUIPMENT'),
        ('M', 'MATERIAL')
        ], string="Type", required=True, readonly=True)
    bim_product_name = fields.Char(string='BIM Name', required=True, readonly=True)
    odoo_product_id = fields.Many2one('product.product', string='Product in Odoo', required=True, domain="[('resource_type','=',type)]")
    odoo_product_code = fields.Char(string='BIM Code', related='odoo_product_id.default_code', readonly=True)

class BimBudgetStageProjection(models.Model):
    _name = 'bim.budget.stage.projection'
    _description = 'Budget Projection By Stage'
    _order = 'stage_start_date asc'

    budget_id = fields.Many2one('bim.budget', readonly=True, ondelete='cascade')
    stage_id = fields.Many2one('bim.budget.stage', domain="[('budget_id', '=', id)]", store=True, ondelete='cascade')
    stage_start_date = fields.Date('Start Date', related='stage_id.date_start', store=True)
    stage_state = fields.Selection('State', related='stage_id.state', store=True)
    budget_at_end = fields.Float('BAC', readonly=True, store=True)
    estimate_at_end = fields.Float('EAC', readonly=True, store=True)
    estimate_up_to_end = fields.Float('ETC', readonly=True, store=True)
    variation_at_end = fields.Float('VAC', readonly=True, store=True)
    work_to_be_done = fields.Float('TCPI', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', related="budget_id.currency_id")


