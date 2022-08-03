# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv.expression import OR


class SaleContractController(http.Controller):
    @http.route('/contract/<model("sale.order"):sale_order>', auth='public', website=True)
    def redirect_contract_report(self, sale_order):
        qr_product_form = request.env['sale.order'].sudo().search([('id','=',sale_order.id)])
        return http.request.render('sat_companies_sale.sale_contract_report',{
            'sale_object': sale_order,
            'name': sale_order.name,
            'pdf_file': sale_order.pdf_file_sale_contract,
            'id_value': sale_order.id
        })

    @http.route(['/get_sale/print_report_contract/'], type='json', auth='public', website=True)
    def print_report_contract(self, id_sale = None):
        if id_sale:
            id_sale = int(id_sale)
            sales = request.env['sale.order'].sudo().search([('id','=',id_sale)])
            return sales.pdf_file_sale_contract.report_action(self)
        else:
            return False
    @http.route(['/get_sale'], type='json', auth='public', website=True)
    def get_sale(self):
        sales = http.request.env['sale.order'].sudo().search([], limit=6)
        s = []
        for sale in sales:
            n = {
                "name": sale.name,
                "id": sale.id
            }
            s.append(n)
        return(s)

    @http.route(['/send_sale'], type='json', auth='public', website=True)
    def send_sale_data(self, url_signature = None, id_sale=None):
        if id_sale and url_signature:
            id_sale = int(id_sale)
            sales = request.env['sale.order'].sudo().search([('id','=',id_sale)])
            for sale in sales:
                sale.signature_url_text = url_signature
                sale.check_signature = True

