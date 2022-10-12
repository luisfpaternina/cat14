# -*- coding: utf-8 -*-
{
    'name': "Invoice payment due letter",

    'summary': """
        Generate and send invoice payment due letters.
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Alberto Touriñán - Process Control",
    'website': "https://www.processcontrol.es",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_due_letter_wizard.xml',
        'views/account_move_views.xml',
        'reports/account_invoice_due_letter.xml',
        'reports/invoice_due_letter.xml',
        'data/mail_invoice_due_letter_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
