# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv.expression import OR


class SuscriptionController(http.Controller):
    @http.route('/welcome/<model("sale.subscription"):sale_subscription>', auth='public', website=True)
    def redirect_contract_report(self, sale_subscription):
        qr_product_form = request.env['sale.subscription'].sudo().search([('id','=',sale_subscription.id)])
        return http.request.render('sat_companies_sale_suscription.welcome_subscription_report',{
            'sale_object': sale_subscription
        })


    @http.route(['/get_sale_subscription/print_report_welcome/'], type='json', auth='public', website=True)
    def print_report_contract(self, id_sale_subscription = None):
        if id_sale_subscription:
            id_sale_subscription = int(id_sale_subscription)
            sales_subs = request.env['sale.subscription'].sudo().search([('id','=',id_sale_subscription)])
            return sales_subs.pdf_file_welcome.report_action(self)
        else:
            return False


    @http.route(['/get_sale'], type='json', auth='public', website=True)
    def get_sale_subscription(self):
        sales_subs = http.request.env['sale.subscription'].sudo().search([], limit=6)
        s = []
        for sale in sales_subs:
            n = {
                "name": sales_subs.name,
                "id": sales_subs.id
            }
            s.append(n)
        return(s)


    @http.route(['/send_sale_subscription'], type='json', auth='public', website=True)
    def send_sale_subscription_data(self, url_signature = None, id_sale_subscription=None):
        if id_sale_subscription and url_signature:
            id_sale_subscription = int(id_sale_subscription)
            sales = request.env['sale.subscription'].sudo().search([('id','=',id_sale_subscription)])
            for sale in sales:
                sale.signature_url_text = url_signature
                sale.check_signature = True
