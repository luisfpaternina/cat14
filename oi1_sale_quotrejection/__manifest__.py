# -*- coding: utf-8 -*-
{
    'name': "oi1_sale_quotrejection",
    'summary': """
        This module will add the option to reject a quotation with a reason and to create a follow up quotation
        """,
    'author': "OntwikkelingInEenvoud (Remko Strating)",
    'website': "http://www.oi1.nl",
	'images': ['static/description/Press the sale reject button.JPG'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],
	'license': 'LGPL-3',
    # always loaded
    'data': [
        'views/sale_order.xml', 
        'views/sale_order_lost_view.xml',  
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
