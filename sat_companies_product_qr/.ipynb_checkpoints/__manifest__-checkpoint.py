# -*- coding: utf-8 -*-
{
    'name': "QR Code Generator Gadgets",
    'summary': """QR Code Generator Gadgets.""",
    'description': """QR Code Generator Gadgets.""",
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'author': "Luis Felipe Paternina",
    'depends': ['base',
                'stock',
                'sat_companies_zones',
                'sat_companies_stock'],
    #'qweb': ['static/src/xml/qr_generator.xml'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
