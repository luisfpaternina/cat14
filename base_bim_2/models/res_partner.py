# coding: utf-8
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _description = "Bim Partner "
    _inherit = 'res.partner'


    # Proyectos ...

    retention_product = fields.Many2one('product.product', 'Product Retention',
                                        help="Product that will be used to bill the Retention")

    project_ids = fields.One2many('bim.project', 'customer_id', 'Projects')
    project_count = fields.Integer('# Projects', compute="_get_project_count")


    def _get_project_count(self):
        for projects in self:
            projects.project_count = len(projects.project_ids)

    def action_view_projects(self):
        projects = self.mapped('project_ids')
        context = self.env.context.copy()
        context.update(default_customer_id=self.id)
        return {
            'type': 'ir.actions.act_window',
            'name': u'Projects',
            'res_model': 'bim.project',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', projects.ids)],
            'context': context
        }


    # Mantenimientos ...

    maintenance_ids = fields.One2many('bim.maintenance', 'partner_id', 'Man')
    maintenance_count = fields.Integer('Maintenance', compute="_get_maintenance_count")

    def _get_maintenance_count(self):
        for maintenances in self:
            maintenances.maintenance_count = len(maintenances.maintenance_ids)

    def action_view_maintenances(self):
        maintenances = self.mapped('maintenance_ids')
        context = self.env.context.copy()
        context.update(default_partner_id=self.id)
        return {
            'type': 'ir.actions.act_window',
            'name': u'Maintenance',
            'res_model': 'bim.maintenance',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', maintenances.ids)],
            'context': context
        }


