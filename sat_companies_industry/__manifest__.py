{
    'name': 'SAT COMPANIES INDUSTRY',

    'version': '14.0.1',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'industry',

    'depends': [

        'maintenance',
        'industry_fsm',
        'sale',
        'project',
        'hr_holidays',
        'base_automation',
        'sale_management',
        'sale_subscription',
        'sat_companies_stock',
        'timesheet_grid',
        'hr_timesheet',
        'sat_companies',
        'sat_companies_zones',

    ],

    'data': [
       
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/project.task.breakdowns.csv',
        'data/ir_filters.xml',
        'data/base_automatization.xml',
        'views/maintenance_minute_point.xml',
        'views/maintenance_type_deffect.xml',
        'views/project_task.xml',
        'views/project_task_ot_checklist.xml',
        'views/project_task_inspection.xml',
        'views/project_task_ot_checklist_location.xml',
        'views/project_task_breakdowns.xml',
        'views/project_task_community_mood.xml',
        'views/project_task_create_timesheet.xml',
        'reports/worksheet.xml',
        'reports/print_qr.xml',
        'reports/technical_data_template.xml',
        'reports/print_gadget_qr.xml',
        'data/sequences.xml',
        'data/ir_rule.xml',
        
    ],
    'installable': True
}
