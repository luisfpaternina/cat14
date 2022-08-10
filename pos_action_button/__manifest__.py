{
    'name': 'pos action button',

    'version': '13.0.0.0',

    'author': "Nybblegroup",

    'website': "",

    'category': 'POS',

    'depends': [

       
        'base',
        'contacts',
        'point_of_sale',

    ],

    'qweb': [

        'static/src/view/action_button.xml'
    ],

    'data': [
       
        'views/res_partner.xml',
                   
    ],
    'installable': True
}
