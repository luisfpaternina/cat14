{
    'name': 'SAT COMPANIES STOCK',

    'version': '14.0.1.0',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'stock',

    'depends': [

        'sale_management',
        'account',
        'project',
        'product',
        'stock',
        'purchase',
        'contacts',
        'sat_companies_partner',
        'sale_subscription',
        'sat_companies_zones',

    ],

    'data': [
       
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/products.xml',
        'views/stock_gadgets.xml',
        'views/stock_gadgets_state.xml',
        'views/stock_gadgets_types_assistance.xml',
        'views/stock_gadgets_use.xml',
        'views/stock_gadgets_contract_type.xml',
        'views/stock_gadgets_increase_type.xml',
        'views/stock_elevator_type.xml',
        'views/stock_soil_type.xml',
        'views/stock_cockpit_keypad.xml',
        'views/stock_cockpit_push.xml',
        'views/stock_shipment.xml',
        'views/stock_bench.xml',
        'views/stock_wash_cabin.xml',
        'views/stock_landing_keypad.xml',
        'views/stock_landing_lock.xml',
        'views/stock_landing_doors.xml',
        'views/stock_maneuvering_table.xml',
        'views/stock_type_cabin_tubes.xml',
        'views/stock_bidirectional_model.xml',
        'views/stock_gsm_model.xml',
        'views/stock_landing_key.xml',
        'views/stock_state_record.xml',
        'views/stock_location.xml',
        'views/stock_inspection_type.xml',
        'reports/technical_data_template.xml',
        
    ],
    'installable': True
}

