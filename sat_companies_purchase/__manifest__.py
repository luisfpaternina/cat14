{
    'name': 'SAT COMPANIES PURCHASE',

    'version': '14.0.1.0',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'stock',

    'depends': [

        'sale_management',
        'stock',
        'purchase',
        'base_automation',

    ],

    'data': [
       
        'security/ir.model.access.csv',
        'data/purchase.order.type.csv',
        'data/po_material_not_arrived.xml',
        'data/base_automatization.xml',
        'views/purchase_order_type.xml',
        'views/purchase_order.xml',
        'reports/purchase_order.xml',
        
    ],
    'installable': True
}
