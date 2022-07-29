{
    'name': 'SAT COMPANIES PARTNER',

    'version': '14.0.1',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'Partner',

    'depends': [

        'contacts',
        'hr',
        'base_automation',
        'base',
        'crm',
        'stock',
        'account_accountant',
        'l10n_latam_base',
        'account',
    ],

    'data': [

        'data/sequences.xml',   
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_delegation.xml',
        'views/res_partner_type.xml',
        'views/res_partner.xml',
        'views/res_partner_communities.xml',
        'views/crm_lead.xml',
        'views/products.xml',
        
    ],
    'installable': True
}
