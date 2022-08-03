# coding: utf-8
from odoo import api, fields, models, _


class BimConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    journal_id = fields.Many2one('account.journal', string='Journal', related="company_id.journal_id", readonly=False)
    working_hours = fields.Float('Workday', related ="company_id.working_hours", readonly=False)
    extra_hour_factor = fields.Float('Overtime Factor', related ="company_id.extra_hour_factor", readonly=False)
    paidstate_product = fields.Many2one('product.product', string='Payment Status Product', related ="company_id.paidstate_product", readonly=False)
    paidstate_product_mant = fields.Many2one('product.product', string='Maintenance Product', related="company_id.paidstate_product_mant", readonly=False)

    retention_product = fields.Many2one('product.product', string='Retention Product',
                                             related="company_id.retention_product", readonly=False)
    retention = fields.Float('Retention %', related="company_id.retention", readonly=False)
    server_hour_difference = fields.Integer('Server Hour Difference', related="company_id.server_hour_difference", readonly=False, required=True)

    validate_stock =fields.Boolean(related="company_id.validate_stock")
    include_vat_in_indicators =fields.Boolean(related="company_id.include_vat_in_indicators", string='Include VAT in Calculations', readonly=False)
    asset_template_id = fields.Many2one('bim.assets.template', related='company_id.asset_template_id', readonly=False)
    stock_location_mobile = fields.Many2one('stock.location', related='company_id.stock_location_mobile', readonly=False)
    type_work = fields.Selection(string="Price in Budget", required=True, related="company_id.type_work", readonly=False)
    array_day_ids = fields.Many2many('bim.maintenance.tags.days', related="company_id.array_day_ids", readonly=False)
    template_mant_id = fields.Many2one('mail.template', related="company_id.template_mant_id", string='Mail Template', readonly=False)
    product_category_id = fields.Many2one('product.category', 'Product Category', related='company_id.bim_product_category_id', readonly=False, required=True)

    # generate_mrp = fields.Boolean('Generar Producción desde Sol. de Materiales', related ="company_id.generate_mrp")
    # expense_type_ids = fields.Many2many('bim.expense.type', string="Gastos Logísticos", related="company_id.expense_type_ids")
    # calendar_id = fields.Many2one('resource.calendar', string='Calendario', related='company_id.bim_calendar_id')
    # follower_ids = fields.Many2many('res.users', string="Seguidores Sol. Materiales", related="company_id.bim_req_follower_ids", help="Seguidores por defecto en las solicitudes de materiales")

    hour_start_job = fields.Selection(related='company_id.hour_start_job', readonly=False, required=True)
    minute_start_job = fields.Selection(related='company_id.minute_start_job', readonly=False, required=True)
    department_required = fields.Boolean(related='company_id.department_required', readonly=False)
    use_project_warehouse = fields.Boolean(related='company_id.use_project_warehouse', readonly=False)
    create_analytic_account = fields.Boolean(related='company_id.create_analytic_account', readonly=False)
    include_picking_cost = fields.Boolean(related='company_id.include_picking_cost', readonly=False)
    warehouse_prefix = fields.Char(related='company_id.warehouse_prefix', readonly=False, required=True)
    invoice_debit_credit = fields.Boolean(related='company_id.invoice_debit_credit', readonly=False)
    limit_certification = fields.Boolean(related='company_id.limit_certification', readonly=False, string="Limit Certification")
    limit_certification_percent = fields.Integer(related='company_id.limit_certification_percent', readonly=False, string="Limit Certification Percent")
    bim_include_invoice_sale = fields.Boolean(related='company_id.bim_include_invoice_sale', readonly=False, string="Bim Include Sale Invoice")
    bim_include_invoice_purchase = fields.Boolean(related='company_id.bim_include_invoice_purchase', readonly=False, string="Bim Include Purchase Invoice")
    bim_include_refund = fields.Boolean(related='company_id.invoice_debit_credit', readonly=False)
    bim_invoice_multiple_project = fields.Boolean(related='company_id.bim_invoice_multiple_project', readonly=False, string="Bim Invoice Multiple Projects")
    bim_certificate_chapters = fields.Boolean(related='company_id.bim_certificate_chapters', readonly=False, string="Certificate Chapters")