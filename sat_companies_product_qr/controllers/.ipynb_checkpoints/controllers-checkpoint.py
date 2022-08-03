# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv.expression import OR


class RespartnerController(http.Controller):
    @http.route('/product/qr-pit/check/<model("product.qr.generator"):product_qr>', auth='users')
    def check_pit_active(self, product_qr):
        qr_product_form = request.env['product.qr.generator'].sudo().search([('id','=',product_qr.id)])
        for record in qr_product_form:
            record.check_pit = True
        return http.request.render('sat_companies_product_qr.product_qr',{
            'product_qr': product_qr.name
        })

    @http.route('/product/qr-cabine/check/<model("product.qr.generator"):product_qr>', auth='public')
    def check_cabine_active(self, product_qr):
        qr_product_form = request.env['product.qr.generator'].sudo().search([('id','=',product_qr.id)])
        for record in qr_product_form:
            record.check_cabine = True
        return http.request.render('sat_companies_product_qr.product_qr',{
            'product_qr': product_qr.name
        })
    
    @http.route('/product/qr-machine/check/<model("product.qr.generator"):product_qr>', auth='public')
    def check_machine_active(self, product_qr):
        qr_product_form = request.env['product.qr.generator'].sudo().search([('id','=',product_qr.id)])
        for record in qr_product_form:
            record.check_machine = True
        return http.request.render('sat_companies_product_qr.product_qr',{
            'product_qr': product_qr.name
        })