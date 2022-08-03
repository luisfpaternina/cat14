# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2017 Marlon Falcón Hernandez
#    (<http://www.ynext.cl>).
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
    'name': 'BIM Base Reporte',
    'version': '14.0.0.1',
    'author': "Ynext",
    'maintainer': 'Ynext',
    'website': 'http://www.ynext.cl',
    'license': 'AGPL-3',
    'category': 'Construction',
    'summary': 'Replace Bim Report Header for Odoo Standard Header',
    'depends': [

    ],
    'description': """
        """,
    'data': [
        'reports/multiple_real_execute_report.xml',
        'reports/quality_control_report.xml',
        'reports/programming_budget_report.xml',
        'reports/budget_report.xml',
        'reports/summary_report.xml',
        'reports/resource_report.xml',
        'reports/checklist_report.xml',
        'reports/certification_report.xml',
         'reports/real_execute_report.xml',
         'reports/report_work_order.xml',
         'reports/maintenance_report.xml',
         'reports/budget_stage_report.xml',
    ],

    'installable': True,
    'auto_install': False,
    'demo': [],
    'test': [],
}
