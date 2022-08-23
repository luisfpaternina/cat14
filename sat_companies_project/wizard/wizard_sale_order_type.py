from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

class WizardSaleOrderType(models.TransientModel):
    _name = 'wizard.sale.order.type'
    _description = 'Tipo de presupuesto'

    name = fields.Char('')
    sale_order_id = fields.Many2one(
        'sale.order',
        'Sale order')
    sale_type_id = fields.Many2one(
        'sale.order.type',
        'Sale order Type')
    is_new_project = fields.Boolean(
        'Is a project existing ?',
        default=True)
    add_task_line = fields.Boolean(
        'Add Task line ?',
        default=True)
    project_id = fields.Many2one(
        'project.project',
        'Project')
    project_line_ids = fields.Many2many(
        'sale.order.line')
    duplicate_task = fields.Boolean(
        'Duplicate Task')
    

    def accept_task_type_sale(self):
        for record in self:
            project_fsm = self.env.ref('industry_fsm.fsm_project', raise_if_not_found=False)
            if record.sale_order_id.sale_order_template_id:
                sale_order_template = record.sale_order_id.sale_order_template_id.name +' - '
            else:
                sale_order_template = ''

            if record.sale_order_id.sale_type_id.is_create_task == True:
                task_ids = record.sale_order_id.sale_type_id.project_task_ids

                new_project = self.env['project.project'].create({
                        'name': sale_order_template +record.sale_order_id.name\
                        +' - '+record.sale_order_id.partner_id.name,
                        'sale_type_origin_id': record.sale_type_id.id,
                        'type_ids': record.sale_type_id.project_stage_ids.ids,
                    })
                
                if task_ids:
                    for task in task_ids:
                        task_value = {
                                'partner_id': record.sale_order_id.partner_id.id,
                                'ot_type_id': record.sale_order_id.sale_type_id.id,
                                'gadgest_contract_type_id': record.sale_order_id.gadgets_contract_type_id.id,
                                'project_id': new_project.id,
                                'allowed_user_ids': record.sale_order_id.allowed_user_ids.ids,
                                'product_id': record.sale_order_id.product_id.id,
                                'origin': record.sale_order_id.name,
                                'comercial_description': record.sale_order_id.comercial_description,
                                #'sale_line_id':record.sale_order_id.id,
                                #'planned_date_begin': record.sale_order_id.date_begin,
                                #'planned_date_end': record.sale_order_id.date_end,
                                #'is_fsm': True,
                                'categ_udn_id': record.sale_order_id.udn_id.id
                                }
                        
                        task.write(task_value)

                        task_names = [x.name for x in project_fsm.task_ids]
                        task_name = record.sale_order_id.name +' - '+task.name
                        if task_name not in task_names:
                            self.env['project.task'].create({
                                'name': record.sale_order_id.name +' - '+task.name,
                                'partner_id': record.sale_order_id.partner_id.id,
                                'ot_type_id': record.sale_order_id.sale_type_id.id,
                                'origin': record.sale_order_id.name,
                                'comercial_description': record.sale_order_id.comercial_description,
                                'gadgest_contract_type_id': record.sale_order_id.gadgets_contract_type_id.id,
                                'project_id': project_fsm.id,
                                'recurring_task': record.sale_order_id.product_id.is_recurring_task,
                                'repeat_interval': record.sale_order_id.product_id.repeat_interval,
                                'repeat_weekday': 'mon',
                                'repeat_unit': record.sale_order_id.product_id.repeat_unit,
                                'repeat_until': record.sale_order_id.product_id.repeat_until,
                                'repeat_number': record.sale_order_id.product_id.repeat_number,
                                #'repeat_type': record.sale_order_id.product_id.repeat_type,
                                'mon': record.sale_order_id.product_id.mon,
                                'tue': record.sale_order_id.product_id.tue,
                                'wed': record.sale_order_id.product_id.wed,
                                'thu': record.sale_order_id.product_id.thu,
                                'fri': record.sale_order_id.product_id.fri,
                                'sat': record.sale_order_id.product_id.sat,
                                'sun': record.sale_order_id.product_id.sun,
                                'allowed_user_ids': record.sale_order_id.allowed_user_ids.ids,
                                'product_id': record.sale_order_id.product_id.id,
                                #'sale_line_id':record.sale_order_id.id,
                                #'planned_date_begin': record.sale_order_id.date_begin,
                                #'planned_date_end': record.sale_order_id.date_end,
                                'is_fsm': True,
                                'categ_udn_id': record.sale_order_id.udn_id.id
                                
                            })

            else:
            
                if not record.sale_order_id.product_id:
                    raise ValidationError(_(
                            'To create a task you must select a Gadget in the quote'
                        ))
                    
                if record.sale_order_id.order_line:
                    for sale_lines in record.sale_order_id.order_line:
                        sale_lines.is_service = True
                        sale_lines.is_expense = False
                
                if record.name and record.sale_type_id and record.sale_order_id:    
                    new_task = self.env['project.task'].create({
                        'name': sale_order_template +record.sale_order_id.name\
                        +' - '+record.sale_order_id.partner_id.name,
                        'partner_id': record.sale_order_id.partner_id.id,
                        'ot_type_id': record.sale_order_id.sale_type_id.id,
                        'origin': record.sale_order_id.name,
                        'comercial_description': record.sale_order_id.comercial_description,
                        'gadgest_contract_type_id': record.sale_order_id.gadgets_contract_type_id.id,
                        'project_id': project_fsm.id,
                        'recurring_task': record.sale_order_id.product_id.is_recurring_task,
                        'repeat_interval': record.sale_order_id.product_id.repeat_interval,
                        'repeat_unit': record.sale_order_id.product_id.repeat_unit,
                        'repeat_until': record.sale_order_id.product_id.repeat_until,
                        'repeat_number': record.sale_order_id.product_id.repeat_number,
                        'repeat_type': record.sale_order_id.product_id.repeat_type,
                        'mon': record.sale_order_id.product_id.mon,
                        'tue': record.sale_order_id.product_id.tue,
                        'wed': record.sale_order_id.product_id.wed,
                        'thu': record.sale_order_id.product_id.thu,
                        'fri': record.sale_order_id.product_id.fri,
                        'sat': record.sale_order_id.product_id.sat,
                        'sun': record.sale_order_id.product_id.sun,
                        'allowed_user_ids': record.sale_order_id.allowed_user_ids.ids,
                        'product_id': record.sale_order_id.product_id.id,
                        #'sale_line_id':record.sale_order_id.id,
                        'planned_date_begin': record.sale_order_id.date_begin,
                        'planned_date_end': record.sale_order_id.date_end,
                        'is_fsm': True,
                        'categ_udn_id': record.sale_order_id.udn_id.id
                        
                    })
                
                if record.sale_order_id.order_line:
                    for sale_lines in record.sale_order_id.order_line:
                        sale_lines.task_id = new_task.id

                
                if record.is_new_project == True:
                    for p in record.project_id:
                        p.write({
                            'type_ids': record.sale_type_id.project_stage_ids.ids,
                            'task_ids': record.sale_type_id.project_task_ids.ids
                        })
                        
                else:
                    self.env['project.project'].create({
                        'name': sale_order_template +record.sale_order_id.name\
                        +' - '+record.sale_order_id.partner_id.name,
                        'sale_type_origin_id': record.sale_type_id.id,
                        'type_ids': record.sale_type_id.project_stage_ids.ids,
                        'task_ids': [
                                        [
                                            0,
                                            0,
                                            {
                                                'name': sale_order_template +record.sale_order_id.name\
                                                +' - '+record.sale_order_id.partner_id.name,
                                                'partner_id': record.sale_order_id.partner_id.id,
                                                'ot_type_id': record.sale_order_id.sale_type_id.id,
                                                'origin': record.sale_order_id.name,
                                                'comercial_description': record.sale_order_id.comercial_description,
                                                'gadgest_contract_type_id': record.sale_order_id.gadgets_contract_type_id.id,
                                                'allowed_user_ids': record.sale_order_id.allowed_user_ids.ids,
                                                'product_id': record.sale_order_id.product_id.id,
                                                #'sale_line_id':record.sale_order_id.id,
                                            }
                                        ]
                                    ]
                    })
            record.sale_order_id.action_confirm()