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
       
        #'security/security.xml',
        #'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/mrp_bom.xml',
                   
    ],
    'installable': True
}
