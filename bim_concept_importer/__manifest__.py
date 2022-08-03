##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2018 Marlon Falcón Hernandez
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
    'name': 'Bim Concept Importer MFH',
    'version': '14.0.1.0.0',
    'author': 'Ynext SpA',
    'maintainer': 'Ynext SpA',
    'website': 'http://www.ynext.cl',
    'license': 'AGPL-3',
    'category': 'Extra Tools',
    'summary': 'Bim Concept Importer.',
    'depends': ['base_bim_2'],
    'data': [
        'views/database_concept_importer.xml',
        'views/work_database_concept_importer.xml',
        'wizard/concept_from_database.xml',
        'views/bim_budget_view.xml',
        'security/security_groups_bim.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
    ],
    'images': ['static/description/banner.jpg'],
}
