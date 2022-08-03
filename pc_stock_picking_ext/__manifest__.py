{
    'name': 'pc stock picking extend',

    "summary": """This module create stock.picking app for users: transfer request""",

    'version': '14.0.0.0',

    'author': "Process Control",

    'website': "www.processcontrol.es",

    'category': 'stock',

    'depends': [

        'base',
        'stock',
        'sat_companies_stock',
        'sat_companies_industry',
        'industry_fsm',

    ],

    'data': [

        'security/security.xml',  
        #'security/ir.model.access.csv',
        'data/send_material_notification.xml',
        'data/send_aswer_material_notification.xml',
        'data/base_automatization.xml',
        'views/stock_picking.xml',
        'views/project_task.xml',
              
    ],
    
    "images": [
        'static/description/icon.png'
    ],
    

    "application": False,
    "installable": True,
    "auto_install": False,

}
