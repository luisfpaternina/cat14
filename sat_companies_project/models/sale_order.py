# -*- coding: utf-8 -*-
from typing import DefaultDict

from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_type_id = fields.Many2one(
        'sale.order.type',
        string="Sale type",
        tracking=True)
    is_potential_client = fields.Boolean(
        string="Is a potential client",
        tracking=True,
        related="partner_id.is_potential_client")
    udn_id = fields.Many2one(
        'project.task.categ.udn',
        string="Udn")
    is_forecast_made = fields.Boolean(
        string="Is forecast made")
    is_maintenance = fields.Boolean(
        string="Is maintenance",
        related="sale_type_id.is_maintenance")
    is_mounting = fields.Boolean(
        string="Is mounting")
    is_normative = fields.Boolean(
        string="Normative",
        related="udn_id.is_normative")
    normative_date = fields.Date(
        string="Normative date")
    comercial_description = fields.Html(
        string="Description")
    project_task_id = fields.Many2one(
        'project.project',
        string="Project task name",
        compute="_compute_check_project_task_id")
    users_ids = fields.Many2many(
                'res.users',
                string='Assigned to')
    

    @api.depends('name','partner_id')
    def _compute_check_project_task_id(self):
        project_obj = self.env['project.project'].search([('name','=','Field Service')],limit=1)
        if project_obj:
            self.project_task_id = project_obj
        else:
            self.project_task_id = False

    @api.onchange(
        'sale_order_type',
        'udn_id')
    def onchange_so_type(self):
        if self.sale_type_id:
            self.is_mounting = self.sale_type_id.is_mounting

    def get_task_sale_type(self):
        for record in self:
            if record.sale_order_template_id:
                sale_order_template = str(record.sale_order_template_id.name+' - ')
            else:
                sale_order_template = ''
            if record.sale_type_id:
                order_type_form = record.env.ref('sat_companies_project.wizard_sale_order_type_form',raise_if_not_found=False)
                ctx = dict(
                    default_name = str(sale_order_template + record.name+' - '+ record.partner_id.name),
                    default_model='wizard.sale.order.type',
                    default_sale_order_id=record.id,
                    default_sale_type_id=record.sale_type_id.id,
                    default_project_line_ids= record.order_line.ids,
                    default_project_id= record.project_task_id.id
                )
                return {
                    'name': ('Tipo de operación'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'wizard.sale.order.type',
                    'views': [(order_type_form.id, 'form')],
                    'view_id': order_type_form.id,
                    'context': ctx,
                    'target': 'new',
                    }
            else:
                record.action_confirm()

    def action_confirm(self):
        state_no_sale = False
        if self.state in ['sent']:
            state_no_sale = True
        res = super(SaleOrder, self).action_confirm()
        for record in self:
            new_state_sale = False
            if self.state in ['sale']:
                new_state_sale = True
            if state_no_sale and new_state_sale:
                project_fsm = self.env.ref('industry_fsm.fsm_project', raise_if_not_found=False)
                if record.sale_order_template_id:
                    sale_order_template = record.sale_order_template_id.name +' - '
                else:
                    sale_order_template = ''

                if record.sale_type_id.is_create_task == True:
                    task_ids = record.sale_type_id.project_task_ids

                    new_project = self.env['project.project'].create({
                            'name': sale_order_template +record.name\
                            +' - '+record.partner_id.name,
                            'sale_type_origin_id': record.sale_type_id.id,
                            'type_ids': record.sale_type_id.project_stage_ids.ids,
                        })
                    
                    
                    if task_ids:
                        for task in task_ids: 
                            task_value = {
                                    'partner_id': record.partner_id.id,
                                    'ot_type_id': record.sale_type_id.id,
                                    'gadgest_contract_type_id': record.gadgets_contract_type_id.id,
                                    'project_id': new_project.id,
                                    'user_id': record.task_user_id.id,
                                    'users_ids': record.users_ids.ids,
                                    'product_id': record.product_id.id,
                                    'recurring_task': record.product_id.is_recurring_task,
                                    'repeat_interval': record.product_id.repeat_interval,
                                    'repeat_unit': record.product_id.repeat_unit,
                                    'repeat_until': record.product_id.repeat_until,
                                    'repeat_number': record.product_id.repeat_number,
                                    #'repeat_type': record.sale_order_id.product_id.repeat_type,
                                    'mon': record.product_id.mon,
                                    'tue': record.product_id.tue,
                                    'wed': record.product_id.wed,
                                    'thu': record.product_id.thu,
                                    'fri': record.product_id.fri,
                                    'sat': record.product_id.sat,
                                    'sun': record.product_id.sun,
                                    'origin': record.name,
                                    'comercial_description': record.comercial_description,
                                    #'sale_line_id':record.sale_order_id.id,
                                    #'planned_date_begin': record.sale_order_id.date_begin,
                                    #'planned_date_end': record.sale_order_id.date_end,
                                    #'is_fsm': True,
                                    'categ_udn_id': record.udn_id.id
                                    }
                            
                            task.write(task_value)
                            if record.tasks_ids:
                                for t in record.tasks_ids:
                                    t.write({
                                    'partner_id': record.partner_id.id,
                                    'ot_type_id': record.sale_type_id.id,
                                    'gadgest_contract_type_id': record.gadgets_contract_type_id.id,
                                    'project_id': project_fsm.id,
                                    'origin': record.name,
                                    'comercial_description': record.comercial_description,
                                    'sale_order_id': record.id,
                                    'user_id': record.task_user_id.id,
                                    'users_ids': record.users_ids.ids,
                                    'product_id': record.product_id.id,
                                    'recurring_task': record.product_id.is_recurring_task,
                                    'repeat_interval': record.product_id.repeat_interval,
                                    'repeat_unit': record.product_id.repeat_unit,
                                    'repeat_until': record.product_id.repeat_until,
                                    'repeat_number': record.product_id.repeat_number,
                                    #'repeat_type': record.sale_order_id.product_id.repeat_type,
                                    'mon': record.product_id.mon,
                                    'tue': record.product_id.tue,
                                    'wed': record.product_id.wed,
                                    'thu': record.product_id.thu,
                                    'fri': record.product_id.fri,
                                    'sat': record.product_id.sat,
                                    'sun': record.product_id.sun,
                                    #'sale_line_id':record.id,
                                    #'planned_date_begin': record.date_begin,
                                    #'planned_date_end': record.date_end,
                                    'categ_udn_id': record.udn_id.id
                                    
                                })

                            task_names = [x.name for x in project_fsm.task_ids]
                            task_name = record.name +' - '+task.name
                            if task_name not in task_names:
                                self.env['project.task'].create({
                                    'name': task_name,
                                    'partner_id': record.partner_id.id,
                                    'ot_type_id': record.sale_type_id.id,
                                    'gadgest_contract_type_id': record.gadgets_contract_type_id.id,
                                    'project_id': project_fsm.id,
                                    'origin': record.name,
                                    'comercial_description': record.comercial_description,
                                    'sale_order_id': record.id,
                                    'user_id': record.task_user_id.id,
                                    'users_ids': record.users_ids.ids,
                                    'product_id': record.product_id.id,
                                    'recurring_task': record.product_id.is_recurring_task,
                                    'repeat_interval': record.product_id.repeat_interval,
                                    'repeat_unit': record.product_id.repeat_unit,
                                    'repeat_until': record.product_id.repeat_until,
                                    'repeat_number': record.product_id.repeat_number,
                                    #'repeat_type': record.sale_order_id.product_id.repeat_type,
                                    'mon': record.product_id.mon,
                                    'tue': record.product_id.tue,
                                    'wed': record.product_id.wed,
                                    'thu': record.product_id.thu,
                                    'fri': record.product_id.fri,
                                    'sat': record.product_id.sat,
                                    'sun': record.product_id.sun,
                                    #'sale_line_id':record.id,
                                    #'planned_date_begin': record.date_begin,
                                    #'planned_date_end': record.date_end,
                                    'is_fsm': True,
                                    'categ_udn_id': record.udn_id.id
                                    
                                })
                if self.is_potential_client:
                    raise ValidationError(_("Verify the type of client if it is potential"))
                    return res
        
        self.update_values_tasks_field_service()
        print('test')

    def update_values_tasks_field_service(self):
        for record in self:
            tasks = self.env['project.task'].search([('origin','=',record.name)])


    @api.onchange(
        'partner_id')
    def onchange_partner(self):
    # plazos de pagos del contacto
        for record in self:
            if record.sale_type_id.is_maintenance:
                record.payment_term_id = record.partner_id.payment_term_maintenance_id
            elif record.sale_type_id.is_line:
                record.payment_term_id = record.partner_id.payment_term_tel_id
            else:
                record.payment_term_id = False
