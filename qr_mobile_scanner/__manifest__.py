{
    'name': 'Qr Code Scanner',

    'version': '13.0.1',

    'author': "",

    'contributors': ['Luis Felipe Paternina'],

    'website': "",

    'depends': [

        'base',
        'web_camera_qrcode_widget',

    ],

    'data': [
       
        'security/ir.model.access.csv',
        'wizard/wizard_qr_mobile_scanner.xml',
        
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}

