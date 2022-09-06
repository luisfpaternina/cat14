# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : MadeUp Infotech (<https://www.madeupinfotech.com/>)
# Copyright(c): 2016-Present MadeUp Infotech
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
    # Application Information
    "name": "Sound Notification Base",
    "category": "Extra Tools",
    'version' : '14.0',
    'license': 'OPL-1',
    
    'summary': """
		Technical base to notify user with the message and sound.
	""",
    'description': """
		Technical base to notify user with the message and sound.
    """,
    
    # Author Information
    'author': 'MadeUp Infotech',
    'maintainer': 'MadeUp Infotech',   
    'website': 'https://www.madeupinfotech.com/',

    # Dependencies
    'depends': ["web","bus","mail"],
    'sequence': 1,

    # Views
    'data': [
        "template/assets.xml",
    ],

    # Application Main Image    
    'images': ['static/description/mu_web_notification_base.png'],

    # Technical
    'installable': True,
    'application' : True,
    'auto_install': False,
    'active': False,
}
