{
    'name': 'SAT COMMISSION MANAGEMENT',

    'version': '14.0.1',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'commission',

    'depends': [

        'sale_management',
        'base',
        'contacts',

    ],

    'data': [
       
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/commissions_view.xml',
        'views/commissions_concepts.xml',
                   
    ],

    "images": [
        'static/description/logo.png'
    ],

    "application": False,
    "installable": True,
    "auto_install": False,
}
