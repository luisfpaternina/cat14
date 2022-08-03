# coding: utf-8
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    journal_id = fields.Many2one('account.journal', string='Journal')
    bim_hours = fields.Integer('Daily Work Hours', default=8)
    validate_stock = fields.Boolean('Validate Stock Movements', default=True)
    working_hours = fields.Float('Working Hours', help="Indicates the number of hours in a day or working day", default=9.0)
    extra_hour_factor = fields.Float('Overtime Factor', digits=(12, 8), help="Indicates the factor for the calculation of overtime", default=0.0077777)
    paidstate_product = fields.Many2one('product.product', 'Payment Status Product', help="Product that will be used to invoice the payment status of project. Leave prices at zero")
    retention_product = fields.Many2one('product.product', 'Retention Product', help="Product that will be used to bill the Retention in the payment status of Project.")
    paidstate_product_mant = fields.Many2one('product.product', 'Maintenance Payment Status', help="Product that will be used to invoice the payment status of the maintenance of Project. Leave Prices at zero")
    stock_location_mobile = fields.Many2one('stock.location', 'Mobile Warehouse Location', help="Location that will be used by default for the entry of merchandise in the Mobile Warehouse")

    retention_product = fields.Many2one('product.product', 'Product Retention',
                                             help="Product to be used to bill the Retention")
    retention = fields.Float('Retention %', default=5)
    type_work = fields.Selection([
        ('cost', 'Cost'),
        ('price', 'Price'),
        ('pricelist', 'Rate'),
        ('costlist', 'Cost List')],
        string="Price in Budget", default='cost')
    asset_template_id = fields.Many2one(
        'bim.assets.template',
        'Assets and Discounts Template',
        default=lambda self: self.env.ref('base_bim_2.bim_asset_template_base', raise_if_not_found=False),
        help='Assets and Discounts template to use when creating a budget')
    array_day_ids = fields.Many2many('bim.maintenance.tags.days')
    template_mant_id = fields.Many2one('mail.template', string='Mail Template')
    bim_product_category_id = fields.Many2one('product.category', required=True, default=lambda self: self.env.ref('product.product_category_all', raise_if_not_found=False))
    include_vat_in_indicators = fields.Boolean()
    hour_start_job = fields.Selection([('0','00'),('1','01'),('2','02'),('3','03'),('4','04'),('5','05'),('6','06'),('7','07'),('8','08'),('9','09'),('10','10'),('11','11'),('12','12'),
                                       ('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),('23','23')], default='9')
    minute_start_job = fields.Selection([('0', '00'), ('05', '05'), ('10', '10'), ('15', '15'), ('20', '20'), ('25', '25'), ('30', '30'),
                                        ('35', '35'), ('40', '40'), ('45', '45'), ('50', '50'), ('55', '55')], default='0')
    department_required = fields.Boolean(default=True)
    use_project_warehouse = fields.Boolean(default=False)
    create_analytic_account = fields.Boolean(default=True)
    include_picking_cost = fields.Boolean(default=False)
    warehouse_prefix = fields.Char(default='ALM ')
    invoice_debit_credit = fields.Boolean(default=True)
    bim_include_invoice_sale = fields.Boolean(default=True, string="Bim Include Sale Invoice")
    bim_include_invoice_purchase = fields.Boolean(default=True, string="Bim Include Purchase Invoice")
    bim_include_refund = fields.Boolean(default=True)
    bim_invoice_multiple_project = fields.Boolean(default=False)
    bim_certificate_chapters = fields.Boolean(default=True, string="Certificate Chapters")
    server_hour_difference = fields.Integer(default=2, string="Server Hour Difference")
    limit_certification_percent = fields.Integer(default=100, string="Limit Certification Percent")
    limit_certification = fields.Boolean(default=True, string="Limit Certification")