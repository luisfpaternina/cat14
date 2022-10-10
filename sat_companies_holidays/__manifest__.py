{
    'name': 'SAT COMPANIES HOLIDAYS',

    'version': '14.0.0.0',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'hr',

    'depends': [

        'base',
        'base_automation',
        'industry_fsm',
        'hr',
        'hr_holidays',
        'project',
        'sat_companies_industry',
        'sat_companies_project',

    ],

    'data': [
       
        'views/project_task.xml',
                   
    ],
    'installable': True
}
