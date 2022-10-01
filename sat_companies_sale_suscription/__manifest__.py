{
    'name': 'SAT COMPANIES SUSCRIPTION',

    'version': '14.0.1',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'stock',

    'depends': [

        'sat_companies',
        'sale_subscription',
        'sat_companies_sale',
        'sat_companies_stock',
        'sat_companies_project',
        'contacts',
        'sale_management'
    ],

    'data': [

        'security/security.xml',
        'security/ir.model.access.csv',
        #'data/stock.gadgets.contract.type.csv',
        'data/subscription.reason.change.csv',
        'data/subscription.inspection.report.csv',
        'data/subscription.process.csv',
        'data/product_template_data.xml',
        'data/contract_suspension.xml',
        'data/contract_extension.xml',
        'data/welcome_template.xml',
        'data/fired_template.xml',
        'data/send_email_low_mto_company.xml',
        'data/send_email_welcome_mto_company.xml',
        'data/base_automatization.xml',
        'views/sale_suscription_template_view.xml',
        'views/sale_order_template.xml',
        'views/sale_subscription.xml',
        'views/sale_order_view.xml',
        'views/res_partner.xml',
        'data/sale.subscription.month.csv',
        'views/sale_subscription_demand.xml',
        'views/subscription_reason_change.xml',
        'views/subscription_inspection_report.xml',
        'views/subscription_process.xml',
        'views/res_company.xml',
        'views/subscription_stage.xml',
        'templates/welcome_template_subscription.xml',
        'data/email_welcome_contract.xml',
        
    ],
    'installable': True
}
