# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Supplier/Vendor Advance payment",
    'summary': """This module will help you handle vendor advance payment on invoiceable lines and down payments odoo app allow to generate purchase advance payment (Fixed/percentage) On purchase order,vendor Advance payment,supplier Advance payment,Purchase advance payment ,Advance Payment Product, Advance down payment purchase""",
    'description': """
This module will help to handle advance payments from vendors in different methods
    """,
    'author': "Globalteckz",
    'website': "http://www.globalteckz.com/shop",
    'category': 'Purchases',
    'version': '14',
    "license" : "Other proprietary",
    'images': ['static/description/Banner.gif'],
    "price": "59.00",
    "currency": "USD",
    'depends': ['base','purchase','sale'],
    'data': [

        'security/ir.model.access.csv',
        'wizard/purchase_make_invoice_advance_view.xml',
        'views/views.xml',
        'views/account_move.xml',
        'data/origin_po_notification.xml',
        'data/base_automatization.xml',

    ],

}
