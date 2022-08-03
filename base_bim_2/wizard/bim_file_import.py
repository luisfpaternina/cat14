from odoo import api, fields, models, _
import tempfile
import base64
import datetime
from bs4 import BeautifulSoup
import io
import csv
import traceback
import os
import xlrd
from io import StringIO
from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError



class BimFileImport(models.TransientModel):
    _name = 'bim.file.import'
    _description = 'Import BIM File'

    budget_id = fields.Many2one('bim.budget', 'Budget')
    filename = fields.Char('File Name')
    bim_file = fields.Binary('File', required=True)
    bim_type = fields.Selection([('revit', 'Revit')], 'BIM File', default='revit', required=True)

    @api.model
    def file_validator(self, fileformat):
        name, extension = os.path.splitext(fileformat)
        return True if extension in ['.csv','.txt'] else False

    def import_bim_file(self):
        if not self.file_validator(self.filename):
            raise UserError(_("File must contain csv or txt extension"))
        file_path = tempfile.gettempdir() + '/bim_file.csv'
        data = self.bim_file
        f = open(file_path, 'wb')
        f.write(base64.b64decode(data))
        # f.write(base64.b64decode(data.decode('utf-16').encode('utf-8')))
        f.close()
        archive = csv.DictReader(open(file_path))
        archive_lines = []
        concept_obj = self.env['bim.concepts']
        index=0
        codes = []
        for line in archive:
            index += 1
            try:
                code = line['Código de montaje']
                qty = line['Recuento']
                if code != '' and qty != '':
                    if code not in codes:
                        codes.append(code)
                        archive_lines.append(line)
                    else:
                        for taken_line in archive_lines:
                            if taken_line['Código de montaje'] == line['Código de montaje']:
                                increment = float(line['Recuento']) + float(taken_line['Recuento'])
                                taken_line['Recuento'] = str(increment)
                                break
            except:
                raise UserError(_("There is an error in line: {}. Please fix it and try again").format(index))

        for line in archive_lines:
            code = line['Código de montaje']
            possible_concept = concept_obj.search([('id_bim','=',code),('budget_id','=',self.budget_id.id)])
            for concept in possible_concept:
                concept.quantity = float(line['Recuento'])
