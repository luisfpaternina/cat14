{
    'name': 'SAT COMPANIES QUALITY',

    'version': '14.0.1',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'Quality',

    'depends': [

        'quality_control',
        'base',

    ],

    'data': [
       
        #'security/security.xml',
        #'security/ir.model.access.csv',
        'reports/nonconformities_report.xml',
        'views/quality_alert.xml',
        
    ],
    'installable': True
}

