# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MultipleLabels(models.Model):
    _name = 'multiple.labels'
    _inherit = 'mail.thread'
    _description = 'Multiple labels'

    label_ids = fields.One2many(
        'multiple.labels.lines',
        'wizard_id',
        string="Gadgets")
    message = fields.Char(
        string="Message")
    formated_date = fields.Char(
        string="Formated date",
        store=True,
        compute='_compute_formate_date')
    day = fields.Char(
        string="Day")
    month = fields.Char(
        string="Month")
    year = fields.Char(
        string="Year")


    @api.depends('create_date')
    def _compute_formate_date(self):
        for product in self:
            if product.create_date:
                dia = str(product.create_date.strftime("%d"))
                mes = str(product.create_date.strftime("%m"))
                anno = str(product.create_date.strftime("%y"))
                format_date = str(dia + ' ' + mes)
                format_date_2 = str(format_date + ' ' + anno)
                product.formated_date = format_date_2
            else:
                product.formated_date = ''


    def action_print(self):
        for rec in self:
            print("Testing! print")



class MultipleLabelsLines(models.Model):
    _name = 'multiple.labels.lines'
    _inherit = 'mail.thread'
    _description = 'Multiple labels lines'

    is_selected = fields.Boolean(
        string="Print",
        default=True)
    wizard_id = fields.Many2one(
        'multiple.labels',
        string="Print wizard")
    product_id = fields.Many2one(
        'product.template',
        string="Gadget",
        related="task_id.product_id")
    task_id = fields.Many2one(
        'project.task',
        string="Task")
