from odoo import models, fields, api
import logging

class WizardSaleOrderType(models.TransientModel):
    _name = 'wizard.sale.order.type'

    name = fields.Char('')
    sale_order_id = fields.Many2one('sale.order', 'Sale order')
    sale_type_id = fields.Many2one('sale.order.type', 'Sale order Type')
    is_new_project = fields.Boolean('Is a project existing ?')
    add_task_line = fields.Boolean('Add Task line ?')
    project_id = fields.Many2one('project.project', 'Project')
    project_line_ids = fields.Many2many('sale.order.line')
    
    
    
    def accept_task_type_sale(self):
        for record in self:
            #project_model = self.env['project.project'].search([('sale_order_id','=',record.sale_order_id.id)])
            if record.is_new_project == True:
                for p in record.project_id:
                    logging.info('*********************IS PROJECTtt')
                    p.write({
                        'type_ids': record.sale_type_id.project_stage_ids.ids,
                        'task_ids': record.sale_type_id.project_task_ids.ids
                    })
                    
            else:
                logging.info('*********************NO IS PROJECTtt')
                self.env['project.project'].create({
                    'name': record.name,
                    'sale_type_origin_id': record.sale_type_id.id,
                    'type_ids': record.sale_type_id.project_stage_ids.ids,
                    'task_ids': record.sale_type_id.project_task_ids.ids
                })
                
            if record.add_task_line == True and record.project_line_ids:
                logging.info('*********************IS TASK')
                for line in record.project_line_ids:
                    logging.info(record.add_task_line)
                    logging.info(record.project_line_ids)
                    logging.info(record.name)
                    logging.info(line.product_id.name)
                    logging.info(record.sale_order_id.partner_id.name)
                    logging.info(record.sale_type_id.name)
                    self.env['project.task'].create({
                        'name': record.name+' - '+line.product_id.name+'TAREA DE LINEA',
                        'partner_id': record.sale_order_id.partner_id.id,
                        'ot_type_id': record.sale_type_id.id 
                    })
                
                
            record.sale_order_id.action_confirm()