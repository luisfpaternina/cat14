# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
import base64 

class RedirectActionNotify(http.Controller):
    @http.route(['/notify/redirect_action'], type='json', auth="user", methods=['POST'])
    def action_notify_redirect_view(self, res_model, res_ids, **kw):
        out = {
            'name': _('Detalle'),
            'type': 'ir.actions.act_window',
            'res_model': res_model,
            'context': {},
            'target' : 'current'
        }
        if len(res_ids) == 1:
            out = dict(out, **{
                'view_mode': 'form',
                'res_id': res_ids[0],
                'views': [
                    [False, "form"],
                ],
            })
        elif len(res_ids) > 1:
            out = dict(out, **{
                'view_mode': 'tree,form',
                'domain': [('id','in',res_ids)],
                'views': [
                    [False, "list"],
                    [False, "form"],
                ]
            })
        else:
            raise ValidationError(_('No se puede procesar el atributo res_ids con valor %s') % res_ids)
        return out
    
    @http.route(['/notify/task-detail'], type='json', auth="user", methods=['POST'])
    def action_notify_play_audio(self, res_model, res_ids, **kw):
        out = {
            'name': _('Detalle'),
            'type': 'ir.actions.act_window',
            'res_model': res_model,
            'context': {},
            'target' : 'current'
        }
        if len(res_ids) == 1:
            out = dict(out, **{
                'view_mode': 'form',
                'res_id': res_ids[0],
                'views': [
                    [False, "form"],
                ],
            })
        elif len(res_ids) > 1:
            out = dict(out, **{
                'view_mode': 'tree,form',
                'domain': [('id','in',res_ids)],
                'views': [
                    [False, "list"],
                    [False, "form"],
                ]
            })
        else:
            raise ValidationError(_('No se puede procesar el atributo res_ids con valor %s') % res_ids)
        return out
    
    @http.route(['/notify/check-notification'], type='json', auth="user", methods=['POST'])
    def action_check_notification(self, res_model, res_ids, **kw):
        task = request.env['project.task'].search([('id','=',res_ids)])
        if task:
            task.task_cheked = True
        

        return False

