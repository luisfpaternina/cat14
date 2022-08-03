from odoo import api, fields, models, _

class LoadTemplateChecklist(models.TransientModel):
    _name = 'load.template.checklist'
    _description = 'Load Checklist Template'

    template_checklist_id = fields.Many2one(comodel_name="bim.master.checklist", string="Template", required=True)

    def load_template(self):
        lines = []
        context = self._context
        project = self.env['bim.project'].browse(context['active_id'])
        for line in self.template_checklist_id.checklist_line_ids:
            values = {
                'sequence': line.sequence,
                'item_id': line.item_id.id,
                'type': line.type
            }
            lines.append([0, 0, values])
        checklist = self.env['bim.checklist'].create({
            'name': self.template_checklist_id.name,
            'project_id': project.id,
            'checklist_line_ids': lines
        })
        return True
