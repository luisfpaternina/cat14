import base64
import datetime
from bs4 import BeautifulSoup

from odoo import fields, models, _
from odoo.exceptions import ValidationError

MS_PREDECESSOR_MAPPING = {
    '0': 'ff',
    '1': 'fs',
    '2': 'sf',
    '3': 'ss',
}


class BimGanttImport(models.TransientModel):
    _name = 'bim.gantt.import'
    _description = 'Import Gantt'

    budget_id = fields.Many2one('bim.budget', 'Budget')
    filename = fields.Char('XML File Name')
    xml_file = fields.Binary('XML File', required=True)
    gantt_type = fields.Selection([('ms', 'Microsoft Project')], 'Gantt Type', default='ms', required=True)
    create_missing = fields.Boolean()
    import_stages = fields.Boolean()
    stage_id = fields.Many2one('bim.budget.stage', 'Stage', domain="[('budget_id', '=', budget_id)]")

    def print_xml(self):
        if self.gantt_type == 'ms':
            return self.load_gantt_ms()
        else:
            raise ValidationError(_('You must choose some gantt format to import.'))

    def load_gantt_ms(self):
        dt_format = '%Y-%m-%dT%H:%M:%S'
        working_hours = self.env.company.working_hours
        file_content = base64.b64decode(self.xml_file)
        content = BeautifulSoup(file_content, 'lxml')
        tasks = [task for task in content.find_all('task') if task.find('wbs')]
        concept_obj = self.env['bim.concepts']
        errors = []
        self.budget_id.do_compute = False
        for task in sorted(tasks, key=lambda t: len(t.find('wbs').text.split('.'))):
            wbs = task.find('wbs')
            # Saltando las 2 primeras tareas
            if wbs and wbs.text in ['0', '1']:
                continue
            concept_id = int(task.find('uid').text)
            concept = self.budget_id.concept_ids.filtered_domain(['&', '|', ('code', '=', wbs.text), ('export_tmp_id', '=', concept_id), ('type', 'in', ['chapter','departure'])])
            if len(concept) > 1:
                concept = concept[0]
            if not concept and not self.create_missing:
                errors.append('<p>The XML file contains the task of ID %d, named %s, and it is not in the budget.</p>' % (concept_id, task.find('name').text))
                continue
            if not concept and self.create_missing:
                code = (wbs and wbs.text or '').split('.')
                concept = concept_obj.create({
                    'code': '.'.join(code),
                    'type': 'chapter' if len(code) <= 2 else 'departure',
                    'name': task.find('name').text,
                    'budget_id': self.budget_id.id,
                    'quantity': 1,
                    'acs_date_start': datetime.datetime.strptime(task.find('start').text, dt_format),
                    'acs_date_end': datetime.datetime.strptime(task.find('finish').text, dt_format),
                })
                if len(code) > 2:
                    parent_code = '.'.join(code[:-1])
                    parent_concept = self.budget_id.concept_ids.filtered_domain([('code', '=', parent_code)])
                    if len(parent_concept) == 1:
                        concept.parent_id = parent_concept

            if self.stage_id and task.find('percentcomplete') and (concept.type_cert == 'stage' or \
                (concept.type_cert != 'stage' and not concept.percent_cert)):
                if concept.type_cert != 'stage':
                    concept.type_cert = 'stage'
                    concept.onchange_type_cert()
                certif_percent = float(task.find('percentcomplete').text)
                if certif_percent:
                    total_cert = sum(concept.certification_stage_ids.mapped('certif_percent'))
                    if total_cert < certif_percent:
                        stage = concept.certification_stage_ids.filtered_domain([('stage_id', '=', self.stage_id.id)])
                        stage.certif_percent = certif_percent - total_cert + stage.certif_percent
                        stage.onchange_percent()
                        concept.update_amount()

            predecessors_vals = []
            predecessors = task.find_all('predecessorlink')
            for pred in predecessors:
                pred_concept_id = int(pred.find('predecessoruid').text)
                pred_concept = self.env['bim.concepts'].search([('budget_id', '=', self.budget_id.id),('export_tmp_id', '=', pred_concept_id), ('type', 'in', ['chapter','departure'])])
                if not pred_concept:
                    pred_name = 'N/A'
                    for ptask in tasks:
                        if ptask.find('uid').text == pred.find('predecessoruid').text:
                            pred_name = ptask.find('name').text
                            break
                    errors.append('<p>The XML file indicates to have the task of ID %d of name %s as a predecessor of the task of ID %d and name %s, and this predecessor does not exist in the budget.</p>' % (pred_concept_id, pred_name, concept_id, task.find('name').text))
                    continue
                predecessors_vals.append((0, 0, {
                    'name': pred_concept.id,
                    'difference': (float(pred.find('linklag').text) / 600 / working_hours) if working_hours else 0,
                    'pred_type': MS_PREDECESSOR_MAPPING.get(pred.find('type').text)
                }))
            concept.bim_predecessor_concept_ids.unlink()
            concept.write({
                'acs_date_start': datetime.datetime.strptime(task.find('start').text, dt_format),
                'acs_date_end': datetime.datetime.strptime(task.find('finish').text, dt_format),
                'bim_predecessor_concept_ids': predecessors_vals,
            })
        if errors:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Import with details',
                    'message': ''.join(errors) + '<b>Close the wizard to see the changes.</b>',
                    'sticky': True,
                    'type': 'warning',
                }
            }
        return {'type': 'ir.actions.act_window_close'}
