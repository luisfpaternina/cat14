from odoo import models, fields, api, _
import xlwt
from io import BytesIO
import base64
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
class BimBudgetMultipleReportWizard(models.TransientModel):
    _name = "bim.budget.multiple.report"
    _description = "Wizard Multiple Report Budget"

    def _default_budget_ids(self):
        budget_ids = self._context.get('active_ids', False)
        budget_obj = self.env['bim.budget']
        project_id = False
        for budget in budget_ids:
            budget_project_id = budget_obj.browse(budget).project_id.id
            if not project_id:
                project_id = budget_project_id
            if project_id != budget_project_id:
                raise UserError(_("You should select only Budgets from the same Project"))
        return budget_ids

    def _default_project_id(self):
        project_id = False
        budget_ids = self._context.get('active_ids', False)
        if len(budget_ids) > 0:
            project_id = self.env['bim.budget'].browse(budget_ids[0]).project_id.id
        return project_id

    project_id = fields.Many2one('bim.project', required=True, default=_default_project_id)
    budget_ids = fields.Many2many('bim.budget', string="Budget", required=True, default=_default_budget_ids, domain="[('project_id','=',project_id)]")

    def generate_multiple_report_xls(self):
        if not self.budget_ids:
            raise UserError(_("You need to select at least one budget"))
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet('Budget')
        file_name = 'Budget'
        style_title = xlwt.easyxf('font: name Times New Roman 180, color-index black, bold on; align: wrap yes, horiz center;')
        style_filter_title = xlwt.easyxf('font: color-index black, bold on; align: wrap yes, horiz center;')
        style_filter_title2 = xlwt.easyxf('align: wrap yes, horiz center;')
        style_summary = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin;')
        style_border_table_top = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin; font: bold on; align: wrap yes, horiz center;')
        style_border_table_bottom = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin; font: bold on;')
        style_border_table_details_chapters = xlwt.easyxf('borders: bottom thin;')
        style_border_table_details_departed = xlwt.easyxf('borders: bottom thin;')
        style_border_table_details = xlwt.easyxf('borders: bottom thin;')

        worksheet.write_merge(0, 0, 0, 13, _("REAL EXECUTION REPORT"), style_title)
        worksheet.write_merge(1,1,0,2, _("Project"),style_filter_title)
        worksheet.write_merge(1,1,3,5, self.project_id.display_name,style_filter_title)
        worksheet.write_merge(1,1,6,8, _("Printing Date"),style_filter_title)

        row = 4
        # Header table
        for budget in self.budget_ids:
            worksheet.write_merge(row,row,9,10, _("BUDGET"), style_border_table_top)
            worksheet.write_merge(row,row,11,13, _("REAL EXECUTED"), style_border_table_top)
            row_to = row + 1
            worksheet.write_merge(row,row_to,14,15, _("DIFFERENCE"), style_border_table_top)
            row += 1
            worksheet.write_merge(row,row,0,1, _("CODE"), style_border_table_top)
            worksheet.write_merge(row,row,2,6, _("CONCEPT"), style_border_table_top)
            worksheet.write_merge(row,row,7,8, _("SUPPLIER"), style_border_table_top)
            worksheet.write_merge(row,row,9,9, _("QUANTITY"), style_border_table_top)
            worksheet.write_merge(row,row,10,10, _("BUDGET"), style_border_table_top)
            worksheet.write_merge(row,row,11,11, _("QUANTITY"), style_border_table_top)
            worksheet.write_merge(row,row,12,12, _("AMOUNT"), style_border_table_top)
            worksheet.write_merge(row,row,13,13, _("REAL"), style_border_table_top)
            # worksheet.write_merge(row,row,15,15, _("DIFFERENCE"), style_border_table_top)
            chapters = budget.concept_ids.filtered(lambda c: not c.parent_id)
            total = 0
            row += 1
            for chapter in chapters:
                balance = round(chapter.balance, 2)
                execute = round(chapter.get_real_executed_for_chapter(True, True, True, True, True),2)
                difference = balance - execute
                worksheet.write_merge(row,row,0,1, chapter.code, style_border_table_details_chapters)
                worksheet.write_merge(row,row,2,6, chapter.name, style_border_table_details_chapters)
                worksheet.write_merge(row,row,7,8, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 9, 9, "-",style_border_table_details_chapters)
                worksheet.write_merge(row, row, 10, 10, chapter.balance,style_border_table_details_chapters)
                worksheet.write_merge(row, row, 11, 11, "-",style_border_table_details_chapters)
                worksheet.write_merge(row, row, 12, 12, "-",style_border_table_details_chapters)
                worksheet.write_merge(row, row, 13, 13, execute,style_border_table_details_chapters)
                worksheet.write_merge(row, row, 14, 15, difference,style_border_table_details_chapters)
                row += 1

                for child in chapter.child_ids:
                    row = self.write_subcharter_level(row, child, worksheet, style_border_table_details_chapters, style_border_table_details_departed)
                    row += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        data_b64 = base64.encodebytes(data)
        doc = self.env['ir.attachment'].create({
            'name': '%s.xls' % (file_name),
            'datas': data_b64,
        })

        return {
            'type': "ir.actions.act_url",
            'url': "web/content/?model=ir.attachment&id=" + str(
                doc.id) + "&filename_field=name&field=datas&download=true&filename=" + str(doc.name),
            'target': "self",
            'no_destroy': False,
        }

    def write_subcharter_level(self,row, sublevel, worksheet, style_border_table_details_chapters, style_border_table_details_departed):
        if sublevel.type == 'chapter':
            balance = round(sublevel.balance, 2)
            execute = round(sublevel.get_real_executed_for_chapter(True, True, True, True, True), 2)
            difference = balance - execute
            worksheet.write_merge(row, row, 0, 1, sublevel.code, style_border_table_details_chapters)
            worksheet.write_merge(row, row, 2, 6, sublevel.name, style_border_table_details_chapters)
            worksheet.write_merge(row, row, 7, 8, "-", style_border_table_details_chapters)
            worksheet.write_merge(row, row, 9, 9, "-", style_border_table_details_chapters)
            worksheet.write_merge(row, row, 10, 10, sublevel.balance, style_border_table_details_chapters)
            worksheet.write_merge(row, row, 11, 11, "-", style_border_table_details_chapters)
            worksheet.write_merge(row, row, 12, 12, "-", style_border_table_details_chapters)
            worksheet.write_merge(row, row, 13, 13, execute, style_border_table_details_chapters)
            worksheet.write_merge(row, row, 14, 15, difference, style_border_table_details_chapters)
        elif sublevel.type == 'departure':
            balance = round(sublevel.balance, 2)
            execute = round(sublevel.get_real_executed_for_chapter(True, True, True, True, True), 2)
            difference = balance - execute
            worksheet.write_merge(row, row, 0, 1, sublevel.code, style_border_table_details_departed)
            worksheet.write_merge(row, row, 2, 6, sublevel.name, style_border_table_details_departed)
            worksheet.write_merge(row, row, 7, 8, "-", style_border_table_details_departed)
            worksheet.write_merge(row, row, 9, 9, sublevel.quantity, style_border_table_details_departed)
            worksheet.write_merge(row, row, 10, 10, sublevel.balance, style_border_table_details_departed)
            worksheet.write_merge(row, row, 11, 11, "-", style_border_table_details_departed)
            worksheet.write_merge(row, row, 12, 12, "-", style_border_table_details_departed)
            worksheet.write_merge(row, row, 13, 13, execute, style_border_table_details_departed)
            worksheet.write_merge(row, row, 14, 15, difference, style_border_table_details_departed)
            parts = sublevel.part_ids.filtered_domain([('state','=','validated')])
            if parts:
                row += 1
                total_parts = sum(part.part_total for part in parts)
                worksheet.write_merge(row, row, 0, 1, " ", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 2, 6, _("PARTS"), style_border_table_details_chapters)
                worksheet.write_merge(row, row, 7, 8, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 9, 9, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 10, 10, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 11, 11, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 12, 12, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 13, 13, total_parts, style_border_table_details_chapters)
                worksheet.write_merge(row, row, 14, 15, "-", style_border_table_details_chapters)
                row += 1
                for part in parts:
                    for part_line in part.lines_ids:
                        worksheet.write_merge(row, row, 0, 1, part.name, style_border_table_details_departed)
                        worksheet.write_merge(row, row, 2, 6, part_line.name.display_name, style_border_table_details_departed)
                        worksheet.write_merge(row, row, 7, 8, part_line.partner_id.display_name if part_line.partner_id else "-", style_border_table_details_departed)
                        worksheet.write_merge(row, row, 9, 9, "-", style_border_table_details_departed)
                        worksheet.write_merge(row, row, 10, 10, "-", style_border_table_details_departed)
                        worksheet.write_merge(row, row, 11, 11, part_line.product_uom_qty, style_border_table_details_departed)
                        worksheet.write_merge(row, row, 12, 12, part_line.price_unit, style_border_table_details_departed)
                        worksheet.write_merge(row, row, 13, 13, part_line.price_subtotal, style_border_table_details_departed)
                        worksheet.write_merge(row, row, 14, 15, "-", style_border_table_details_departed)
                        row += 1
                row -= 1
            concept_attendances = sublevel.get_concept_attendance_records()
            if concept_attendances:
                row += 1
                worksheet.write_merge(row, row, 0, 1, " ", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 2, 6, _("ATTENDANCE"), style_border_table_details_chapters)
                worksheet.write_merge(row, row, 7, 8, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 9, 9, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 10, 10, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 11, 11, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 12, 12, "-", style_border_table_details_chapters)
                worksheet.write_merge(row, row, 13, 13, concept_attendances[1], style_border_table_details_chapters)
                worksheet.write_merge(row, row, 14, 15, "-", style_border_table_details_chapters)
                for attendance in concept_attendances[0]:
                    row += 1
                    worksheet.write_merge(row, row, 0, 1, "", style_border_table_details_departed)
                    worksheet.write_merge(row, row, 2, 6, attendance.employee_id.display_name,style_border_table_details_departed)
                    worksheet.write_merge(row, row, 7, 8,"-",style_border_table_details_departed)
                    worksheet.write_merge(row, row, 9, 9, "-", style_border_table_details_departed)
                    worksheet.write_merge(row, row, 10, 10, "-", style_border_table_details_departed)
                    worksheet.write_merge(row, row, 11, 11, attendance.worked_hours,style_border_table_details_departed)
                    worksheet.write_merge(row, row, 12, 12, attendance.attendance_cost / attendance.worked_hours if attendance.worked_hours>0 else '',style_border_table_details_departed)
                    worksheet.write_merge(row, row, 13, 13, attendance.attendance_cost,style_border_table_details_departed)
                    worksheet.write_merge(row, row, 14, 15, "-", style_border_table_details_departed)
        return row