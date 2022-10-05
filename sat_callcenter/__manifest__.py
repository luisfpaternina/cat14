# -*- coding: utf-8 -*-
{
    'name': "SAT CALLCENTER",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Alberto Touriñán - Process Control",
    'website': "https://www.processcontrol.es/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'project',
        'industry_fsm',
        'sat_companies_industry',
        'sat_companies_project',
        'hr_timesheet',
        'pc_stock_picking_ext',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/sat_callcenter_security.xml',
        'views/project_task_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
