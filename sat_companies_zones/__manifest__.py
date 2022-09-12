{
    'name': 'SAT COMPANIES ZONES',

    'version': '14.0.1',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'Partner',

    'depends': [

        'contacts',
        'hr',
        'stock',
        'sat_companies_partner',
        'sat_companies_hr',
        'sat_companies_zones',

    ],

    'data': [
       
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'views/res_partner_zone.xml',
        'views/res_partner_route.xml',
        'views/res_partner_guard_zone.xml',
        'data/sequences.xml',
        
    ],
    'installable': True
}

