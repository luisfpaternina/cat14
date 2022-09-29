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
    
    @http.route(['/notify/playsound'], type='json', auth="user", methods=['POST'])
    def action_notify_redirect_view(self, res_model, res_ids, **kw):
        res_ids = res_ids[0]
        user = request.env['res.users'].search([('id','=',res_ids)])
        audio_user = user.audio_notification_task
        audio_enc=base64.b64encode(audio_user)
        if not audio_user:
            raise ValidationError(_('The User does not have audio file upload '))
        
        
        result = audio_enc
        #result = dict(**{
        #        'audio_enc': audio_enc
        #        })
        return result

