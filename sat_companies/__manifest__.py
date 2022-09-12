{
    'name': 'SAT COMPANIES',

    'version': '14.0.1',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'Maintenance',

    'depends': [

        'sale_management',
        'contacts',
        'account_accountant',
        'account',
        'sale_subscription',
        'crm',
        'base',
        'base_automation',
        'industry_fsm',
        'sat_companies_stock',
        'hr',
        'mrp',

    ],

    'data': [
       
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/account_move_line.xml',
        'views/res_partner.xml',
        'views/mrp_bom.xml',
        'views/views_res_config_settings.xml',
        'views/project_task.xml',
        'reports/invoice.xml',
        'reports/inherit_sale_order.xml',
        'data/account_receipt.xml',
                   
    ],
    'installable': True
}
