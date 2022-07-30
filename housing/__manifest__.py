{
    'name': 'Housing',

    'version': '14.0.0.0',

    'author': "Luis Felipe Paternina",

    'website': "",

    'category': 'helpdesk',

    'depends': [

       
        'base',
        'helpdesk',
        'contacts',
        'sale_management',

    ],

    'data': [
       
        'views/res_partner.xml',
        'views/sale_order.xml',
                   
    ],
    'installable': True
}
