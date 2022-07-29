{
    'name': 'SAT COMPANIES HR',

    'version': '14.0.1.0',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'Partner',

    'depends': [

        'contacts',
        'hr',
        'hr_holidays',
        'sat_companies_partner',
        'base_automation',
        'stock',

    ],

    'data': [
       
       'security/security.xml',
       'security/ir.model.access.csv',
       'views/hr_employee.xml',
       'views/hr_employee_category.xml',
       'views/hr_employee_type.xml',
       'data/sequences.xml',
        
    ],
    'installable': True
}

