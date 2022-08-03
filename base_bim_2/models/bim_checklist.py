# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
class BimMasterChecklist(models.Model):
    _name = 'bim.master.checklist'
    _description = 'Checklist Template'

    code = fields.Char(string='Code', readonly=True, index=True, default=lambda self: 'New', required=True)
    name = fields.Char(string='Name', required=True)
    checklist_line_ids = fields.One2many("bim.master.checklist.line", "checklist_id", string="List", required=True)

    @api.model
    def create(self, vals):
        if vals.get('code', "New") == "New":
            vals['code'] = self.env['ir.sequence'].next_by_code('bim.master.checklist') or "New"
        return super(BimMasterChecklist, self).create(vals)

class BimChecklistState(models.Model):
    _name = 'bim.checklist.state'
    _description = 'Bim Checklist State'
    _order = "sequence asc, id desc"

    name = fields.Char(required=True, translate=True)
    is_new = fields.Boolean()
    is_done = fields.Boolean()
    sequence = fields.Integer(default=16)
    user_ids = fields.Many2many('res.users', string="Users")
    notify = fields.Boolean(default=False)

class BimMasterChecklistLine(models.Model):
    _name = 'bim.master.checklist.line'
    _description = 'Checklist Template Lines'

    item_id = fields.Many2one(comodel_name="bim.checklist.items", string='Description', required=True)
    type = fields.Selection(string="Type", selection=[('check', 'Check'),
                                                      ('yesno', 'Yes / No'),
                                                      ('txt', 'Text'),
                                                      ('int', 'Numeric Value')], default="check")
    checklist_id = fields.Many2one("bim.master.checklist", string="Checklist")
    sequence = fields.Integer(string='Sequence', default=10)

class BimChecklist(models.Model):
    _name = 'bim.checklist'
    _description = 'Bim Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string='Name')
    code = fields.Char(string='Code', readonly=True, index=True, default=lambda self: 'Name', required=True)
    date = fields.Date('Date',default=fields.Date.today)
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible', default=lambda self: self.env.user)
    project_id = fields.Many2one("bim.project", string="Project")
    checklist_line_ids = fields.One2many("bim.checklist.line", "checklist_id", string="List")
    checklist_image_ids = fields.One2many("bim.checklist.images", "checklist_id", string="Images")
    obs = fields.Text(string="Observations")
    digital_signature = fields.Binary(string='Signature')
    state_id = fields.Many2one('bim.checklist.state', string='State', index=True, tracking=True,
        compute='_compute_state_id', readonly=False, store=True,
        copy=False, ondelete='restrict', default=lambda s: s.env['bim.checklist.state'].search([], limit=1))

    def _compute_state_id(self):
        state_obj = self.env['bim.checklist.state']
        for checklist in self:
            if not checklist.state_id:
                checklist.state_id = state_obj.search([], order='sequence asc').id

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id.user_ids:
            if self.env.user.id not in self.state_id.user_ids.ids:
                users = ""
                for user in self.state_id.user_ids:
                    users += user.display_name + ", "
                raise UserError(_("Only users {} can set current Checklist to state {}").format(users[:-2], self.state_id.name))
            if self.state_id.notify:
                message = self.notify_to_state_users()
                if len(message) > 1:
                    record = self.browse(self.ids[0])
                    record.message_post(body=_("Checklist State Change notification sent to: {}").format(message))

    def notify_to_state_users(self):
        email_to = ''
        message = ''
        for user in self.state_id.user_ids:
            if user.partner_id.email:
                email_to += user.partner_id.email + ','
                message += user.partner_id.name + ' - ' + user.partner_id.email + ', '
        if len(email_to) > 1:
            email_to = email_to[:-1]
        template_id = self.env.ref('base_bim_2.email_template_checklist_notification').id
        template = self.env['mail.template'].browse(template_id)
        template['email_to'] = email_to
        template.send_mail(self.ids[0], force_send=True)
        return message

    @api.model
    def create(self, vals):
        if vals.get('code', "New") == "New":
            vals['code'] = self.env['ir.sequence'].next_by_code('bim.checklist') or "New"
        return super(BimChecklist, self).create(vals)

    def action_checklist_send(self):
        '''
        Esta Function abre una ventana con una plantilla de correo para enviar el Checklist por correo
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('base_bim_2', 'email_template_checklist')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'bim.checklist',
            'active_model': 'bim.checklist',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'mark_so_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, ctx['default_model'], [ctx['default_res_id']])
        self = self.with_context(lang=lang)

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class BimChecklistLine(models.Model):
    _name = 'bim.checklist.line'
    _description = 'List Checklist'

    @api.model
    def default_get(self, default_fields):
        values = super(BimChecklistLine, self).default_get(default_fields)
        values['sequence'] = len(self.checklist_id.checklist_line_ids) + 1
        return values

    item_id = fields.Many2one("bim.checklist.items", string='Description', required=True)
    is_ready = fields.Boolean(string='Status')
    is_ready_c = fields.Char(string='Value')
    #notes_id = fields.Many2one(comodel_name="bim.checklist.notes", string="Observations")
    checklist_id = fields.Many2one("bim.checklist", string="Checklist")
    sequence = fields.Integer(string='Sequence')
    type = fields.Selection([
        ('check', 'Check'),
        ('yesno', 'Yes / No'),
        ('txt', 'Text'),
        ('int', 'Numeric Value')],string="Type")


class BimChecklistImages(models.Model):
    _name = 'bim.checklist.images'
    _description = 'Images Checklist'
    _inherit = ['image.mixin']

    name = fields.Char(string='Description')
    checklist_id = fields.Many2one('bim.checklist', string='Checklist')

class BimChecklistNotes(models.Model):
    _name = 'bim.checklist.items'
    _description = 'Items Checklist'

    name = fields.Text(string='Description')


