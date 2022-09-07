{
    'name': 'SAT COMPANIES MRP',

    'version': '14.0.0.0',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'MRP',

    'depends': [

        'sale_management',
        'base',
        'mrp',
        'sat_companies',
        'sat_companies_industry',

    ],

    'data': [

        'views/sale_order.xml',
        'views/mrp_bom.xml',
        'reports/inherit_report_mrp_bom.xml',

                   
    ],
    'installable': True
}
