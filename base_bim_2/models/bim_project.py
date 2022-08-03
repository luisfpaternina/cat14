# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.
import base64

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.modules.module import get_module_resource

class BimTag(models.Model):
    _name = 'bim.tag'
    _description = 'Bim Tag'

    active = fields.Boolean(default=True)
    color = fields.Integer(required=True, default=0)
    name = fields.Char(required=True)

class BimProjectState(models.Model):
    _name = 'bim.project.state'
    _description = 'Bim Project State'
    _order = "sequence asc, id desc"

    name = fields.Char(required=True, translate=True)
    is_new = fields.Boolean()
    is_done = fields.Boolean()
    include_in_attendance = fields.Boolean(default=True, string="Include in Attendance")
    sequence = fields.Integer(default=16)
    user_ids = fields.Many2many('res.users', string="Users")

class bim_project(models.Model):
    _description = "Project"
    _name = 'bim.project'
    _order = "id desc"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    @api.depends('timesheet_ids')
    def _compute_timesheet_count(self):
        for project in self:
            project.timesheet_count = len(project.timesheet_ids)

    @api.depends('document_ids')
    def _compute_count_docs(self):
        for project in self:
            project.count_docs = len(project.document_ids)

    @api.depends('objects_ids')
    def _compute_count_objects(self):
        for project in self:
            project.count_objects = len(project.objects_ids)

    @api.depends('task_ids')
    def _compute_count_tasks(self):
        for project in self:
            project.task_done_count = len(project.task_ids.filtered(lambda r: r.state == 'end'))
            project.count_tasks = len(project.task_ids.filtered(lambda r: r.state != 'cancel'))

    @api.depends('ticket_ids')
    def _compute_count_tickets(self):
        for project in self:
            project.ticket_done_count = len(project.ticket_ids.filtered(lambda r: r.state == 'calificado'))
            project.count_tickets = len(project.ticket_ids.filtered(lambda r: r.state != 'cancel'))

    @api.depends('employee_line_ids')
    def _compute_employee_count(self):
        for project in self:
            project.employee_count = len(project.employee_line_ids)

    def _compute_requisition(self):
        for project in self:
            project.requisition_count = len(self.env['bim.purchase.requisition'].search([('project_id','=',project.id)]))

    @api.depends('paidstate_ids')
    def _compute_paidstate(self):
        for project in self:
            project.paidstatus_count = len(project.paidstate_ids)

    @api.depends('budget_ids')
    def _get_budget_count(self):
        for project in self:
            project.budget_count = len(project.budget_ids)

    @api.depends('maintenance_ids')
    def _compute_maintenance(self):
        for project in self:
            project.maintenance_done_count = len(project.maintenance_ids.filtered(lambda r: r.state == 'done' or r.state == 'invoiced'))
            project.maintenance_count = len(project.maintenance_ids)

    @api.depends('invoice_ids')
    def _compute_invoice(self):
        for project in self:
            invoices = project.invoice_ids
            out_invoices = invoices.filtered(lambda i: i.state != 'cancel' and i.move_type == 'out_invoice')
            in_invoices = invoices.filtered(lambda i: i.state != 'cancel' and i.move_type == 'in_invoice')
            refunds = invoices.filtered(lambda i: i.state != 'cancel' and i.move_type == 'out_refund')
            in_refunds = invoices.filtered(lambda i: i.state != 'cancel' and i.move_type == 'in_refund')
            project.out_invoice_count = len(out_invoices)
            project.in_invoice_count = len(in_invoices)
            project.out_invoiced_amount = sum(x.amount_total for x in out_invoices) - sum(x.amount_total for x in refunds)
            project.in_invoiced_amount = sum(x.amount_total for x in in_invoices) - sum(x.amount_total for x in in_refunds)

    @api.depends('budget_ids','budget_ids.balance','budget_ids.surface','budget_ids.state_id.include_in_amount')
    def _compute_amount(self):
        for project in self:
            project.balance = sum(x.balance for x in project.budget_ids.filtered_domain([('state_id.include_in_amount','=',True)]))
            project.surface = sum(x.surface for x in project.budget_ids)

    @api.depends('budget_ids')
    def _compute_hh(self):
        for project in self:
            project.hh_planificadas = 0

    @api.depends('stock_location_id')
    def _compute_valuation(self):
        quant_obj = self.env['stock.quant']
        for project in self:
            if project.stock_location_id:
                quants = quant_obj.search([('location_id', '=', project.stock_location_id.id)])
                project.inventory_valuation = sum(q.value for q in quants)
            else:
                project.inventory_valuation = 0

    @api.depends('stock_location_id')
    def _compute_outgoing_val(self):
        picking_obj = self.env['stock.picking']
        for project in self:
            if project.stock_location_id:
                pickings = picking_obj.search([
                    ('bim_project_id','=',project.id),
                    ('location_dest_id.usage','=','customer')])
                if pickings:
                    project.outgoing_val = sum(picking.total_cost for picking in pickings)
                else:
                    project.outgoing_val = 0
            else:
                project.outgoing_val = 0
    @api.model
    def _default_image(self):
        image_path = get_module_resource('base_bim_2', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    @api.depends('state_id')
    def _get_project_state(self):
        for record in self:
            record.project_state = 'in_process'

    @api.depends('outsourcing_ids')
    def _compute_outsourcing_count(self):
        for project in self:
            project.outsourcing_count = len(project.outsourcing_ids)

    @api.depends('checklist_ids')
    def _compute_chekclist_count(self):
        for project in self:
            project.checklist_count = len(project.checklist_ids)

    @api.depends('workorder_ids')
    def _compute_workorder_count(self):
        for project in self:
            project.workorder_count = len(project.workorder_ids)

    @api.depends('balance', 'surface')
    def _compute_balance_surface(self):
        for record in self:
            if record.surface != 0:
                balace_surface = record.balance / record.surface
            else:
                balace_surface = 0.0
            record.balace_surface = balace_surface


    def compute_executed_attendance_and_cost(self):
        for record in self:
            executed = 0
            cost = 0
            for line in record.project_attendance_ids:
                executed += line.worked_hours
                cost += line.attendance_cost
            record.executed_attendance = executed
            record.attendance_cost = cost

    @api.depends('project_cost_ids','project_cost_ids.amount', 'balance')
    def compute_total_project_cost(self):
        for record in self:
            total = 0
            for line in record.project_cost_ids:
                total += line.amount
            record.total_project_cost = total
            record.total_project_cost_difference = record.balance - total

    @api.depends('sale_project_cost_ids', 'sale_project_cost_ids.amount')
    def compute_sale_total_project_cost(self):
        for record in self:
            total = 0
            for line in record.sale_project_cost_ids:
                total += line.amount
            record.sale_total_project_cost = total

    def compute_project_profit(self):
        for record in self:
            record.project_profit = record.sale_total_project_cost - record.total_project_cost

    def compute_project_margin(self):
        for record in self:
            record.project_margin = (1 - (record.total_project_cost / record.sale_total_project_cost)) * 100 if record.sale_total_project_cost > 0 else 0

    # Datos
    name = fields.Char('Code', default="New", tracking=True, copy=False)
    nombre = fields.Char('Name', tracking=True, copy=True)
    notes = fields.Text(string="Observations")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company, required=True )
    user_id = fields.Many2one('res.users', string='Supervisor', tracking=True,  default=lambda self: self.env.user)
    task_ids = fields.One2many('bim.task', 'project_id', 'Tasks')
    ticket_ids = fields.One2many('ticket.bim', 'project_id', 'Ticket')
    obs = fields.Text('Notes')
    retention = fields.Float('Retención %', default=lambda self: self.env.company.retention)
    image_1920 = fields.Image("Image", max_width=1920, max_height=1920, default=_default_image)
    image_128 = fields.Image("Image 128", max_width=128, max_height=128, store=True, default=_default_image)
    budget_count = fields.Integer('N° Budgets', compute="_get_budget_count")
    budget_ids = fields.One2many('bim.budget','project_id','Budgets')
    hh_planificadas = fields.Float('HH Planned', compute="_compute_hh")
    currency_id = fields.Many2one('res.currency', required=True, default=lambda r: r.env.company.currency_id)
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    invoice_address_id = fields.Many2one('res.partner', string='Invoice Address', tracking=True)

    def write(self, values):
        res = super().write(values)
        if 'analytic_id' in values and self.analytic_id:
            other_projects = self.search([('analytic_id','=',self.analytic_id.id),('id','!=',self.id)])
            if other_projects:
                analytic = self.analytic_id
                raise UserError(_("It is not possible to assign Analytic Account {} because it is already in use in Project {}").format(analytic.display_name, other_projects[0].display_name))
        return res

    @api.onchange('customer_id')
    def onchange_customer_id(self):
        cost_obj = self.env['bim.cost.list']
        for record in self:
            invoice_addr = False
            if self.env.company.type_work == 'costlist':
                if record.customer_id:
                    cost_list = cost_obj.search([('partner_id','=',record.customer_id.id)], limit=1)
                    if not cost_list and record.customer_id.state_id:
                        cost_list = cost_obj.search([('state_id', '=', record.customer_id.state_id.id)], limit=1)
                    if cost_list:
                        record.cost_list_id = cost_list.id
                    else:
                        record.cost_list_id = False
            if record.analytic_id:
                record.analytic_id.partner_id = record.customer_id.id
            if record.customer_id.child_ids:
                for child in record.customer_id.child_ids.filtered_domain([('type','=','invoice')]):
                    invoice_addr = child.id
                    break
            if invoice_addr:
                record.invoice_address_id = invoice_addr
            else:
                record.invoice_address_id = record.id

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    stock_location_id = fields.Many2one('stock.location', string='Stock Location')
    country_id = fields.Many2one('res.country', string='Country')
    street_id = fields.Many2one('res.partner', string='Address')
    date_ini = fields.Date('Start Date', default=fields.Date.today)
    date_end = fields.Date('End Date')
    date_ini_real = fields.Date('Start Date Real')
    date_end_real = fields.Date('End Date Real')
    expedient = fields.Char('Proceedings', translate=True)
    date_contract = fields.Date('Contract Date', help="Contract Date")
    adjudication_date = fields.Date('Award date')
    document_ids = fields.One2many('bim.documentation','project_id','Documents')
    objects_ids = fields.One2many('bim.object', 'project_id', 'Objects')
    count_docs = fields.Integer('Quantity Documents', compute="_compute_count_docs")
    count_objects = fields.Integer('Quantity Objets', compute="_compute_count_objects")
    count_tasks = fields.Integer('Quantity Tasks', compute="_compute_count_tasks")
    count_tickets = fields.Integer('Quantity Tickets', compute="_compute_count_tickets")
    task_done_count = fields.Integer('Quantity Executed Tasks', compute="_compute_count_tasks")
    ticket_done_count = fields.Integer('Quantity Executed Tickets', compute="_compute_count_tickets")
    timesheet_count = fields.Integer('Quantity Time Sheet', compute="_compute_timesheet_count")
    timesheet_ids = fields.One2many('bim.project.employee.timesheet', 'project_id', 'Hours Employees')
    employee_count = fields.Integer('Quantity Employees', compute="_compute_employee_count")
    employee_line_ids = fields.One2many('bim.project.employee', 'project_id', 'Employee Lines')
    requisition_count = fields.Integer('Quantity Material Requests', compute="_compute_requisition")
    paidstate_ids = fields.One2many('bim.paidstate','project_id','Payment Status')
    paidstatus_count = fields.Integer('Quantity EP', compute="_compute_paidstate")
    paidstate_product = fields.Many2one('product.product', string='Payment Status Product', default=lambda self: self.env.company.paidstate_product)
    retention_product = fields.Many2one('product.product', string='Retention Product', default=lambda self: self.env.company.retention_product)
    department_id = fields.Many2one('bim.department', string='Departament')
    maintenance_ids = fields.One2many('bim.maintenance', 'project_id', 'Maintenance')
    maintenance_done_count = fields.Integer('Quantity Executed Maintenance', compute="_compute_maintenance")
    maintenance_count = fields.Integer('Quantity Maintenance Total', compute="_compute_maintenance")
    invoice_ids = fields.One2many('account.move', 'project_id', 'Invoices')
    out_invoice_count = fields.Integer('Quantity Sale Invoices', compute="_compute_invoice")
    in_invoice_count = fields.Integer('Quantity Purchase Invoices', compute="_compute_invoice")
    out_invoiced_amount = fields.Monetary('Sales Invoiced Amount', compute="_compute_invoice")
    in_invoiced_amount = fields.Monetary('Purchases Invoiced Amount', compute="_compute_invoice")
    outgoing_val = fields.Monetary('Income by Deliveries', compute="_compute_outgoing_val")
    inventory_valuation = fields.Monetary('Inventory Valuation', compute="_compute_valuation")
    expense_val = fields.Monetary('Calculation Surrender',)# compute="_compute_expenses")
    amount_award = fields.Monetary('Award Amount',)
    amount_tender = fields.Monetary('Bid Amount',)
    analytic_created = fields.Boolean('Cost Center Created', help="Indicates if the project cost centers have already been created")
    maintenance_contract = fields.Boolean('Maintenance Contract')
    analytic_id = fields.Many2one('account.analytic.account','Cost Center')
    tag_ids = fields.Many2many('bim.tag', string='Tags')
    outsourcing_count = fields.Integer('Subcontracts', compute="_compute_outsourcing_count")
    outsourcing_ids = fields.One2many('bim.project.outsourcing', 'project_id', 'Subcontract expenses')
    maintenance = fields.Boolean("Maintenance Created", default=False)
    maintenance_amount = fields.Monetary('Total Contract Amount', help="Total amount of the maintenance contract")
    maintenance_duration = fields.Integer('Maintenance duration', help="Estimated duration of each maintenance in days", default=1)
    maintenance_start_date = fields.Date('Start Date', help="Start Date of maintenance contract")
    maintenance_end_date = fields.Date('End Date', help="End Date of maintenance contract")
    maintenance_currency_id = fields.Many2one('res.currency', 'Currency', default=lambda r: r.env.user.company_id.currency_id)
    surface = fields.Float(string="Surface m2", compute='_compute_amount', help="Builded surface (m2).", store=True)
    balance = fields.Monetary(string="Balance", compute='_compute_amount', help="General Balance of the Budget.", store=True)
    balace_surface = fields.Monetary(string="Balance /m2", compute=_compute_balance_surface, help="Balance per m2")
    indicator_ids = fields.One2many('bim.project.indicator', 'project_id', 'Comparative indicators')
    color = fields.Integer('Index Color', default=0)
    priority = fields.Selection(
        [('1', 'Low'),
         ('2', 'Medium'),
         ('3', 'High'),
         ('4', 'Very High'),
         ('5', 'Urgent'),
         ], 'Priority', default='1', help="Project Priority")

    maintenance_period = fields.Selection(
        [('12', 'Monthly'),
         ('2', 'Biannual'),
         ('1', 'Annual'),
         ('3', 'Quarterly'),
         ('6', 'Bimonthly'),
         ], 'Frequency', default='12', help="Frequency of collection of the maintenance contract")
    project_state = fields.Selection(
        [('in_process', 'Awarded'),('cancel', 'Lost')],
        string='Tracking Status',compute="_get_project_state", store=True)

    state_id = fields.Many2one(
        'bim.project.state', string='State', index=True, tracking=True,
        compute='_compute_state_id', readonly=False, store=True,
        copy=False, ondelete='restrict', default= lambda s: s.env['bim.project.state'].search([], limit=1))
    cost_list_id = fields.Many2one('bim.cost.list')
    use_cost_list = fields.Boolean(compute='_giveme_cost_list')

    def _giveme_cost_list(self):
        if self.env.company.type_work == 'costlist':
            self.use_cost_list = True
        else:
            self.use_cost_list = False

    def _compute_state_id(self):
        state_obj = self.env['bim.project.state']
        for project in self:
            if not project.state_id:
                project.state_id = state_obj.search([], limit=1).id

    checklist_ids = fields.One2many('bim.checklist', 'project_id', 'Checklists')
    checklist_count = fields.Integer('N° Checklists', compute="_compute_chekclist_count")
    workorder_ids = fields.One2many('bim.work.order', 'project_id', 'Work Orders')
    workorder_count = fields.Integer('N° Work Orders', compute="_compute_workorder_count")
    price_agreed_ids = fields.One2many('bim.list.price.agreed', 'project_id', string='Agreed Prices')
    project_attendance_ids = fields.One2many('hr.attendance', 'project_id' )
    executed_attendance = fields.Float(compute='compute_executed_attendance_and_cost')
    attendance_cost = fields.Float(compute='compute_executed_attendance_and_cost')
    project_cost_ids = fields.One2many('bim.project.cost', 'project_id', readonly=True)
    sale_project_cost_ids = fields.One2many('bim.project.sale', 'project_id', readonly=True)
    total_project_cost = fields.Monetary(string='Project Cost', compute='compute_total_project_cost')
    total_project_cost_difference = fields.Monetary(string='Cost Difference', compute='compute_total_project_cost')
    sale_total_project_cost = fields.Monetary(string='Sales', compute='compute_sale_total_project_cost')
    project_profit = fields.Monetary(string='Benefit', compute='compute_project_profit')
    project_margin = fields.Float(string='Margin %', compute='compute_project_margin')
    accounting_ids = fields.One2many('account.move', 'project_id', domain="[('bim_classification','=','income')]")
    incomes_value = fields.Integer(compute='compute_incomes_expenses')
    expenses_value = fields.Integer(compute='compute_incomes_expenses')
    department_required = fields.Boolean(default=lambda self: self.env.company.department_required)
    purchase_ids = fields.One2many('purchase.order','project_id')
    purchase_count = fields.Integer(compute='compute_purchase_count')
    opening_balance_ids = fields.One2many('bim.opening.balance','project_id')
    opening_balance_total = fields.Integer(compute='compute_opening_balance_count', store=True)
    quality_control_plan_ids = fields.One2many('bim.quality.control.plan', 'project_id')
    quality_control_plan_count = fields.Integer(compute='compute_quality_control_plan_count')
    active = fields.Boolean(default=True)

    @api.depends('quality_control_plan_ids')
    def compute_quality_control_plan_count(self):
        for record in self:
            record.quality_control_plan_count = len(record.quality_control_plan_ids)

    @api.depends('opening_balance_ids','opening_balance_ids.active')
    def compute_opening_balance_count(self):
        for record in self:
            balance = 0
            for bal_rec in record.opening_balance_ids.filtered_domain([('active','=',True)]):
                balance += bal_rec.amount
            record.opening_balance_total = balance

    def compute_purchase_count(self):
        for record in self:
            record.purchase_count = len(record.purchase_ids)

    def compute_incomes_expenses(self):
        for record in self:
            total_inc = 0
            total_exp = 0
            for move in record.accounting_ids:
                if move.bim_classification == 'income' and move.state == 'posted':
                    total_inc += move.amount_total
                elif move.bim_classification == 'expense' and move.state == 'posted':
                    total_exp += move.amount_total
            record.incomes_value = total_inc
            record.expenses_value = total_exp

    def action_view_quality_control_plan(self):
        plans = self.mapped('quality_control_plan_ids')
        action = self.env.ref('base_bim_2.action_bim_quality_control').sudo().read()[0]
        if len(plans) == 0:
            action['context'] = {'default_project_id': self.id}
            action['views'] = [(False, 'form')]
        else:
            action['domain'] = [('id', 'in', plans.ids)]
            action['context'] = {'default_project_id': self.id}
        return action

    def action_view_opening_balance(self):
        balances = self.mapped('opening_balance_ids')
        action = self.env.ref('base_bim_2.action_bim_opening_balance').sudo().read()[0]
        if len(balances) == 0:
            action['context'] = {'default_project_id': self.id}
            action['views'] = [(False, 'form')]
        else:
            action['domain'] = [('id', 'in', balances.ids)]
            action['context'] = {'default_project_id': self.id}
        return action

    def action_view_purchases(self):
        purchases = self.mapped('purchase_ids')
        context = self.env.context.copy()
        context.update(default_project_id=self.id)
        return {
            'type': 'ir.actions.act_window',
            'name': u'Compras',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', purchases.ids)],
            'context': context
        }

    def action_view_incomes(self):
        accounting_ids = self.mapped('accounting_ids')
        action = self.env.ref('account.action_move_journal_line').sudo().read()[0]
        if len(accounting_ids) == 0:
            action['accounting_ids'] = {'default_project_id': self.id, 'default_bim_classification': 'income'}
            action['views'] = [(False, 'form')]
        else:
            incomes = []
            for income in accounting_ids:
                if income.bim_classification == 'income' and income.state == 'posted':
                    incomes.append(income.id)
            action['domain'] = [('id', 'in', incomes)]
            action['context'] = {'default_project_id': self.id, 'default_bim_classification': 'income'}
        return action

    def action_view_expenses(self):
        accounting_ids = self.mapped('accounting_ids')
        action = self.env.ref('account.action_move_journal_line').sudo().read()[0]
        if len(accounting_ids) == 0:
            action['context'] = {'default_project_id': self.id, 'default_bim_classification': 'expense'}
            action['views'] = [(False, 'form')]
        else:
            expenses = []
            for expense in accounting_ids:
                if expense.bim_classification == 'expense' and expense.state == 'posted':
                    expenses.append(expense.id)
            action['domain'] = [('id', 'in', expenses)]
            action['context'] = {'default_project_id': self.id, 'default_bim_classification': 'expense'}
        return action

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id.user_ids and self.env.user.id not in self.state_id.user_ids.ids:
            users = ""
            for user in self.state_id.user_ids:
                users += user.display_name + ", "
            raise UserError(
                _("Only users {} can set current Project to state {}").format(users[:-2], self.state_id.name))

    @api.onchange('warehouse_id','stock_location_id')
    def onchange_stock(self):
        if not self.stock_location_id and self.warehouse_id:
            self.stock_location_id = self.warehouse_id.lot_stock_id.id

        if not self.warehouse_id:
            self.stock_location_id = False

        if self.stock_location_id:
            warehouse = self.env['stock.warehouse'].search([('lot_stock_id','=',self.stock_location_id.id)],limit=1)
            if warehouse and self.warehouse_id != warehouse:
                self.warehouse_id = warehouse.id

    @api.onchange('date_end','date_ini')
    def onchange_date(self):
        if not self.date_ini:
           datetime.now()

        if self.date_end and self.date_end <= self.date_ini:
            warning = {
                'title': _('Warning!'),
                'message': _(u'The End Date cannot be less than the start date!'),
            }
            self.date_end = False
            return {'warning': warning}

    def action_create_maintenance(self):
        fmt = '%Y-%m-%d'
        for project in self:
            if project.maintenance_amount <= 0.0:
                raise ValidationError(_('The amount of the maintenance contract cannot be zero (0)'))
            if not project.maintenance_period:
                raise ValidationError(_('Select the periodicity of the maintenance contract'))
            if not project.maintenance_start_date:
                raise ValidationError(_('Enter a maintenance start date'))
            date_start = datetime.strptime(str(project.maintenance_start_date), fmt).replace(hour=8, minute=00)
            date_end = datetime.strptime(str(project.maintenance_end_date), fmt).replace(hour=23, minute=59)
            maintenance_obj = self.env['bim.maintenance']
            dif = date_end - date_start
            frequency = int(dif.days/30.417)/int(project.maintenance_period)
            for i in range(int(project.maintenance_period)):
                index = i+1
                maintenance_date = index == 1 and date_start or date_start + relativedelta(months=round(frequency))
                maintenance_obj.create({
                    'project_id': project.id,
                    'partner_id': project.customer_id.id,
                    'maintenance_duration': project.maintenance_duration,
                    'date_planned': maintenance_date,
                    'date_done': maintenance_date + relativedelta(days=project.maintenance_duration),
                    'invoice_amount': project.maintenance_amount/int(project.maintenance_period)
                })
                date_start = maintenance_date
            project.maintenance = True

    def create_warehouse(self):
        for project in self:
            vals = {
                'name': project.company_id.warehouse_prefix + ' ' + project.nombre,
                'code': project.name[-4:],
                'partner_id': project.customer_id and project.customer_id.id or False,
            }
            warehouse = self.env['stock.warehouse'].sudo().create(vals)
            project.warehouse_id = warehouse.id
            project.stock_location_id = warehouse.lot_stock_id.id

    def create_project_object(self):
        for project in self:
            vals = {
                'desc': project.name + ' ' + project.nombre,
                'project_id': project.id,
            }
            self.env['bim.object'].sudo().create(vals)


    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":

            code = self.env['ir.sequence'].sudo().next_by_code('bim.project') or "New"
            # Creamos la cuenta anaitica por cada proyecto creado
            if self.env.company.create_analytic_account:
                analytic = self.env['account.analytic.account'].sudo().create({'name': vals['nombre'],
                                                                        'partner_id': vals['customer_id'],
                                                                    'code': code})
                vals['analytic_id'] = analytic.id
            vals['name'] = code

        project = super(bim_project, self).create(vals)
        project.create_project_object()
        return project

    def name_get(self):
        res = super(bim_project, self).name_get()
        result = []
        for element in res:
            project_id = element[0]
            cod = self.browse(project_id).name
            desc = self.browse(project_id).nombre
            name = cod and '[%s] %s' % (cod, desc) or '%s' % desc
            result.append((project_id, name))
        return result

    def action_view_attendance(self):
        project_attendance_ids = self.mapped('project_attendance_ids')
        action = self.env.ref('hr_attendance.hr_attendance_action').sudo().read()[0]
        if len(project_attendance_ids) == 0:
            action['context'] = {'default_project_id': self.id}
            action['views'] = [(False, 'form')]
        else:
            action['domain'] = [('id', 'in', project_attendance_ids.ids)]
            action['context'] = {'default_project_id': self.id}
        return action

    def action_view_budgets(self):
        budgets = self.mapped('budget_ids')
        action = self.env.ref('base_bim_2.action_bim_budget').sudo().read()[0]
        if len(budgets) > 0:
            action['domain'] = [('id', 'in', budgets.ids)]
            action['context'] = {'default_project_id': self.id,'default_currency_id': self.currency_id.id}
            return action
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'New Budget',
                'res_model': 'bim.budget',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_project_id': self.id,'default_currency_id': self.currency_id.id}
            }

    def action_view_requisitions(self):
        requsitions = self.env['bim.purchase.requisition'].search([('project_id','=',self.id)])
        action = self.env.ref('base_bim_2.action_bim_purchase_requisition').sudo().read()[0]
        action['domain'] = [('id', 'in', requsitions.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_timesheets(self):
        timesheets = self.mapped('timesheet_ids')
        action = self.env.ref('base_bim_2.action_bim_project_timesheet').sudo().read()[0]
        if len(timesheets) > 0:
            action['domain'] = [('id', 'in', timesheets.ids)]
        else:
            action = {
                'type': 'ir.actions.act_window',
                'res_model': 'bim.project.employee.timesheet',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_projects_id': self.id}
            }
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_timesheets(self):
        timesheets = self.mapped('timesheet_ids')
        action = self.env.ref('base_bim_2.action_bim_project_timesheet').sudo().read()[0]
        if len(timesheets) > 0:
            action['domain'] = [('id', 'in', timesheets.ids)]
        else:
            action = {
                'type': 'ir.actions.act_window',
                'res_model': 'bim.project.employee.timesheet',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_projects_id': self.id}
            }
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_outsourcing(self):
        outsourcings = self.mapped('outsourcing_ids')
        action = self.env.ref('base_bim_2.action_bim_project_outsourcing').sudo().read()[0]
        action['domain'] = [('id', 'in', outsourcings.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_employees(self):
        employees = self.mapped('employee_line_ids')
        action = self.env.ref('base_bim_2.action_bim_project_employee').sudo().read()[0]
        action['domain'] = [('id', 'in', employees.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_documents(self):
        documents = self.mapped('document_ids')
        action = self.env.ref('base_bim_2.action_bim_documentation').sudo().read()[0]
        action['domain'] = [('id', 'in', documents.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_objects(self):
        bim_objects = self.mapped('objects_ids')
        action = self.env.ref('base_bim_2.action_bim_object').sudo().read()[0]
        action['domain'] = [('id', 'in', bim_objects.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_checklist(self):
        checklists = self.mapped('checklist_ids')
        action = self.env.ref('base_bim_2.bim_checklist_action').sudo().read()[0]
        action['domain'] = [('id', 'in', checklists.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_workorder(self):
        workorders = self.mapped('workorder_ids')
        action = self.env.ref('base_bim_2.action_work_orders_project').sudo().read()[0]
        action['domain'] = [('id', 'in', workorders.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_tasks(self):
        tasks = self.mapped('task_ids')
        action = self.env.ref('base_bim_2.action_bim_task').sudo().read()[0]
        action['domain'] = [('id', 'in', tasks.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_tickets(self):
        tickets = self.mapped('ticket_ids')
        action = self.env.ref('base_bim_2.action_ticket_bim').sudo().read()[0]
        action['domain'] = [('id', 'in', tickets.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_out_invoices(self):
        invoices = []
        for inv in self.invoice_ids:
            if inv.move_type == 'out_invoice':
                invoices.append(inv.id)
        action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        if len(invoices) > 0:
            action['domain'] = [('id', 'in', invoices)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_in_invoices(self):
        invoices = []
        for inv in self.invoice_ids:
            if inv.move_type == 'in_invoice':
                invoices.append(inv.id)
        action = self.env.ref('account.action_move_in_invoice_type').sudo().read()[0]
        if len(invoices) > 0:
            action['domain'] = [('id', 'in', invoices)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_outgoings(self):
        action = {'type': 'ir.actions.act_window_close'}
        if self.stock_location_id:
            pickings = self.env['stock.picking'].search([
                ('bim_project_id','=',self.id),
                ('location_dest_id.usage','=','customer'),
            ])
            pickings += self.env['stock.picking'].search([
                ('bim_project_id', '=', self.id),
                ('location_id.usage', '=', 'customer'),('returned', '=', True)
            ])
            if len(pickings) > 0:
                action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
                action['domain'] = [('id', 'in', pickings.ids)]
        return action

    def action_view_quants(self):
        action = self.env.ref('stock.dashboard_open_quants').sudo().read()[0]
        action['domain'] = [('location_id', '=', self.stock_location_id.id)]
        action['context'] = {'search_default_productgroup': 1, 'search_default_internal_loc': 1}
        return action

    def action_view_paidstate(self):
        paidstate = self.mapped('paidstate_ids')
        action = self.env.ref('base_bim_2.action_bim_paidstate').sudo().read()[0]
        action['domain'] = [('id', 'in', paidstate.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_maintenance(self):
        maintenance = self.mapped('maintenance_ids')
        action = self.env.ref('base_bim_2.action_bim_maintenance').sudo().read()[0]
        action['domain'] = [('id', 'in', maintenance.ids)]
        action['context'] = {'default_project_id': self.id}
        return action

    def update_project_cost(self):
        for line in self.project_cost_ids:
            line.unlink()
        # Creando líneas para costos de Asistencia
        total = 0
        cost_obj = self.env['bim.project.cost']
        include_vat = self.company_id.include_vat_in_indicators
        for attendance in self.project_attendance_ids:
            total += attendance.attendance_cost
        if total > 0:
            cost_obj.create({
                'project_id': self.id,
                'type': 'attendance',
                'amount': total
            })
        ##Creando líneas para costos de Facturacion
        total = 0
        invoice_lines = self.env['account.move.line'].search(
            [('analytic_account_id', '=', self.analytic_id.id), ('move_id.move_type', 'in', ['in_invoice','in_refund']),
             ('product_id', '!=', False),('move_id.state','=','posted')])
        for line in invoice_lines:
            if line.move_id.include_for_bim:
                if line.move_id.move_type == 'in_invoice':
                    total += line.price_total if include_vat else line.price_subtotal
                else:
                    total -= line.price_total if include_vat else line.price_subtotal
        if total > 0:
            cost_obj.create({
                'project_id': self.id,
                'type': 'purchase_invo',
                'amount': total
            })

        ##Creando líneas para apuntes contables
        total = 0
        moves_expenses = self.env['account.move'].search([('bim_classification','=','expense'),('state','=','posted'),('include_for_bim','=',True)])
        for move in moves_expenses:
            take_it = False
            for line in move.line_ids:
                if line.analytic_account_id == self.analytic_id:
                    take_it = True
                    break
            if take_it:
                total += move.amount_total

        if total > 0:
            cost_obj.create({
                'project_id': self.id,
                'type': 'other',
                'amount': total
            })

        total = 0
        for budget in self.budget_ids:
            for concept in budget.concept_ids.filtered(lambda c: c.type == 'departure'):
                for part in concept.part_ids.filtered(lambda c: c.state == 'validated'):
                    for line in part.lines_ids:
                        total += line.price_subtotal
        if total > 0:
            cost_obj.create({
                'project_id': self.id,
                'type': 'report',
                'amount': total
            })

        # aqui vamos a tomar los costos de las entregas
        picking_obj = self.env['stock.picking']
        domain = [('bim_project_id', '=', self.id), ('picking_type_code', '=', 'outgoing'), ('state', '=', 'done'),('include_for_bim', '=', True)]
        pickings = picking_obj.search(domain)
        total = 0
        for picking in pickings:
            total += picking.total_cost
        domain = [('bim_project_id', '=', self.id), ('picking_type_code', '=', 'incoming'), ('state', '=', 'done'), ('returned', '=', True),('include_for_bim', '=', True)]
        pickings = picking_obj.search(domain)
        for picking in pickings:
            total -= picking.total_cost

        if total > 0:
            cost_obj.create({
                'project_id': self.id,
                'type': 'delivery',
                'amount': total
            })

        #aqui metemos los saldos de apertura
        total = 0
        for bal in self.opening_balance_ids:
            total += bal.amount

        if total > 0:
            cost_obj.create({
                'project_id': self.id,
                'type': 'open',
                'amount': total
            })
        return True

    def update_sale_project_cost(self):
        for line in self.sale_project_cost_ids:
            line.unlink()
        # Creando líneas para costos de Asistencia
        total = 0
        cost_obj = self.env['bim.project.sale']
        include_vat = self.company_id.include_vat_in_indicators
        ##Creando líneas para costos de Facturacion
        invoice_lines = self.env['account.move.line'].search(
            [('analytic_account_id', '=', self.analytic_id.id), ('move_id.move_type', 'in', ['out_invoice','out_refund']),
             ('product_id', '!=', False),('move_id.state','=','posted')])
        for line in invoice_lines:
            if line.move_id.include_for_bim:
                if line.move_id.move_type == 'out_invoice':
                    total += line.price_total if include_vat else line.price_subtotal
                else:
                    total -= line.price_total if include_vat else line.price_subtotal
        if total > 0:
            cost_obj.create({
                'project_id': self.id,
                'type': 'sale_invo',
                'amount': total
            })

        total = 0
        moves_incomes = self.env['account.move'].search(
            [('bim_classification', '=', 'income'), ('state', '=', 'posted'),('include_for_bim','=',True)])
        for move in moves_incomes:
            take_it = False
            for line in move.line_ids:
                if line.analytic_account_id == self.analytic_id:
                    take_it = True
                    break
            if take_it:
                total += move.amount_total

        if total > 0:
            cost_obj.create({
                'project_id': self.id,
                'type': 'other',
                'amount': total
            })

        return True


class BimProjectOutsourcing(models.Model):
    _description = "Work Subcontracts Expenses"
    _name = 'bim.project.outsourcing'
    _rec_name = 'partner_id'

    name = fields.Char('Description')
    partner_id = fields.Many2one('res.partner', 'Supplier')
    project_id = fields.Many2one('bim.project', 'Project')
    reference = fields.Char('Reference EP')
    date = fields.Date('Date', default=fields.Date.today())
    amount = fields.Monetary('Balance')
    outsourcing_amount = fields.Monetary('Total')
    currency_id = fields.Many2one('res.currency', string='Currency',
        readonly=True, default=lambda r: r.env.user.company_id.currency_id)


class bim_project_employee(models.Model):
    _description = "Construction Employees"
    _name = 'bim.project.employee'
    _order = 'start_date asc'

    project_id = fields.Many2one('bim.project', 'Project', domain="[('company_id','=',company_id)]")
    employee_id = fields.Many2one('hr.employee', 'Employee')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
        default=lambda self: self.env.company, required=True)


class bim_project_employee_timesheet(models.Model):
    _description = "Construction Employees"
    _name = 'bim.project.employee.timesheet'
    _rec_name = 'employee_id'
    _order = 'week_start desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id and self.task_id:
            self.project_id = self.task_id.project_id.id

    @api.model
    def default_get(self, fields):
        res = super(bim_project_employee_timesheet, self).default_get(fields)
        today = date.today()
        start = today - timedelta(days=today.weekday())
        res['week_start'] = datetime.strftime(start, '%Y-%m-%d')
        res['week_end'] = datetime.strftime((start + timedelta(days=6)), '%Y-%m-%d')
        return res

    project_id = fields.Many2one('bim.project', 'Project', domain="[('company_id','=',company_id)]")
    task_id = fields.Many2one('bim.task', 'Task')
    date = fields.Date('Date', default=fields.Date.today)
    week_start = fields.Date('Start Week')
    week_end = fields.Date('End Week')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    total_hours = fields.Float('Total Hours')
    total_extra_hours = fields.Float('Total Extra Hours')
    week_number = fields.Integer('Week Number', compute='compute_week_number', store=True)
    work_cost = fields.Float('Labor Cost', compute='compute_work_cost')
    extra_work_cost = fields.Float('Labor Cost HE', help="Cost of overtime labor", compute='compute_work_cost')
    comment = fields.Text('Comments')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company, required=True )

    @api.depends('employee_id', 'total_hours')
    def compute_work_cost(self):
        for record in self:
            wage = record.employee_id.wage_bim
            hour_wage = (wage / 30) / self.env.user.company_id.working_hours
            record.work_cost = hour_wage * record.total_hours
            record.extra_work_cost = wage * self.env.user.company_id.extra_hour_factor * record.total_extra_hours

    @api.depends('week_start')
    def compute_week_number(self):
        for record in self:
            if record.week_start:
                today = date.today()
                year = int(record.week_start.year)
                month = int(record.week_start.month)
                day = int(record.week_start.day)
                number_week = date(year, month, day).strftime("%V")
                record.week_number = number_week


class bim_obra_indicator(models.Model):
    _description = "Comparative indicators"
    _name = 'bim.project.indicator'

    @api.depends('projected', 'budget')
    def _compute_percent(self):
        for record in self:
            record.percent = record.budget > 0.0 and (record.projected / record.budget * 100) or 0.0

    @api.depends('real', 'projected')
    def _compute_diff(self):
        for record in self:
            record.projected = record.budget - record.real

    project_id = fields.Many2one('bim.project', 'Project', ondelete="cascade")
    currency_id = fields.Many2one('res.currency', 'Currency', related="project_id.currency_id")
    type = fields.Selection(
        [('M', 'Material Cost'),
         ('Q', 'Equipment Cost'),
         ('H', 'Labor Cost'),
         ('S', 'Sub-Contract Cost'),
         ('HR', 'Tools Costs'),
         ('LO', 'Logistic Cost'),
         ('T', 'Total'), ],
        'Indicator Type', readonly=True)

    budget = fields.Monetary('Budjet', help="Budget Amount", readonly=True)
    real = fields.Monetary('Real Certified', help="Actual value represented in the awarded budget", readonly=True)
    projected = fields.Float('Projected', help="Difference between projected and actual", compute="_compute_diff")
    percent = fields.Float('%', help="Percentage given by the real value between the estimated value", compute="_compute_percent")


class BimProjectCost(models.Model):
    _description = "Project Cost"
    _name = 'bim.project.cost'

    type = fields.Selection([('attendance','Attendance'),('delivery','Deliveries'),('report','Project Report'),('purchase_invo','Purchase Invoices'),('open','Opening Balance'),('other','Other expenses')], string='Type')
    amount = fields.Monetary(string='Amount')
    project_id = fields.Many2one('bim.project')
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id')

class BimProjectCost(models.Model):
    _description = "Project Sales"
    _name = 'bim.project.sale'

    type = fields.Selection([('sale_invo','Sale Invoices'),('other','Other Incomes')], string='Type')
    amount = fields.Monetary(string='Amount')
    project_id = fields.Many2one('bim.project')
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id')