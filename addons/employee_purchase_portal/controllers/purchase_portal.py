# -*- coding: utf-8 -*-

import base64
from collections import OrderedDict

import odoo
from odoo import http, _
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
from odoo.addons.portal.controllers.portal import \
    pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Home
from odoo.addons.web.controllers.main import Binary
from odoo.addons.web.controllers.main import ensure_db
from odoo.tools import image_process

from odoo.exceptions import AccessError, MissingError

import logging
_logger = logging.getLogger(__name__)

import requests
from odoo.exceptions import ValidationError

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_decode, iri_to_uri


class PurchasePortalController(CustomerPortal):
    def _prepare_home_portal_values(self):
        values = super(PurchasePortalController, self)._prepare_home_portal_values()
        
        # Domain to filter records as per user group
        domain = []
        user = request.env.user
        if user.has_group('employee_purchase_portal.group_purchase_approver'):
            domain += [
                ('order_sequence', '=', False)
            ]
        else:
            domain += [
                ('order_sequence', '=', False),
                ('user_id', '=', request.env.user.id)
            ]

        values['purchase_count'] = request.env['purchase.order'].search_count(domain)
        return values

    def _purchase_order_get_page_view_values(self, order, access_token, **kwargs):
        
        def resize_to_48(b64source):
            if not b64source:
                b64source = base64.b64encode(Binary().placeholder())
            return image_process(b64source, size=(48, 48))

        values = {
            'order': order,
            'resize_to_48': resize_to_48,
        }
        return self._get_page_view_values(order, access_token, values, 
            'my_purchases_history', True, **kwargs)


    @http.route([
        '/my/purchase', 
        '/my/purchase/page/<int:page>'], 
        type='http', 
        auth="user", 
        website=True)
    def portal_my_purchase_orders(self, page=1, date_begin=None, 
        date_end=None, sortby=None, filterby=None, **kw):

        values = dict()
        purchase_maker = request.env.user
        PurchaseOrder = request.env['purchase.order']

        domain = []

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        }
        
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Domain as per user group
        user_domain = []
        user = request.env.user
        if user.has_group('employee_purchase_portal.group_purchase_approver'):
            user_domain += [
                ('order_sequence', '=', False)
            ]
        else:
            user_domain += [
                ('order_sequence', '=', False),
                ('user_id', '=', request.env.user.id)
            ]

        searchbar_filters = {
            'no_order_sequence': {
                'label': _('My Orders'), 
                'domain': user_domain
            },
        }

        # default filter by value
        if not filterby:
            filterby = 'no_order_sequence'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        purchase_count = PurchaseOrder.search_count(domain)
        
        # make pager
        pager = portal_pager(
            url="/my/purchase",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=purchase_count,
            page=page,
            step=self._items_per_page
        )
        
        # search the purchase orders to display, according to the pager data
        orders = PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        
        request.session['my_purchases_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'purchase',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/purchase',
        })
        return request.render("purchase.portal_my_purchase_orders", values)


    @http.route(['/my/purchase/<int:order_id>'], type='http', auth="public", website=True)
    def portal_my_purchase_order(self, order_id=None, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('purchase.order', order_id, 
                access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._purchase_order_get_page_view_values(order_sudo, access_token, **kw)
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id
        return request.render("purchase.portal_my_purchase_order", values)


    @http.route([
        '''/my/purchase/request_form'''
    ], type='http', auth='public', website=True)
    def request_purchase_form(self, **kw):

        # Current user
        user = request.env.user

        # Model environments
        product_categ_env = request.env['product.category']
        product_product_env = request.env['product.product']

        # List of allowed product categories
        allowed_product_categs = product_categ_env.search([
            ('id', 'in', user.partner_id.allowed_product_categories.ids)
        ])

        # List of allowed products
        allowed_products = product_product_env.search([
            ('categ_id', 'in', allowed_product_categs.ids)
        ])

        # Prepare vals for the purchase order
        order_vals = {}

        # Check current user group
        if not user.has_group('employee_purchase_portal.group_purchase_approver'):
            order_vals['user_id'] = user.id
        else:
            raise AccessError("You are not allowed to make purchase request.")

        return request.render(
            "employee_purchase_portal.portal_create_purchase_order", 
            {
                'allowed_products': allowed_products,
            } 
        )


    @http.route([
        '''/my/purchase/vendor'''
    ], type='http', auth='public', website=True)
    def select_vendor(self, **kw):

        # Models Environment
        product_supplier_env = request.env['product.supplierinfo']
        product_template_env = request.env['product.template']

        # Selected product
        selected_product = request.env['product.product'].search([
            ('id', '=', kw['portal_product_id'])
        ])

        # List of available vendors
        available_vendors = product_supplier_env.search([
            ('product_tmpl_id', '=', selected_product.product_tmpl_id.id)])

        return request.render(
            "employee_purchase_portal.portal_select_vendor", 
            {
                'selected_product_id': selected_product.id,
                'product_qty': int(kw['product_qty']),
                'vendors': available_vendors,
            } 
        )


    @http.route([
        '''/my/purchase/create'''
    ], type='http', auth='public', website=True)
    def create_purchase_order(self, **kw):

        # Vals for Purchase Request
        create_vals = {}
        
        # Vendor Details    
        supplier_info = request.env['product.supplierinfo'].search([
            ('id', '=', kw['supplier_info'])])
        partner_id = request.env['res.partner'].search([
            ('id', '=', supplier_info.name.id)
        ])

        # Type casting to integer to avoid type incoherence
        create_vals['portal_product_id'] = int(kw['selected_product_id'])
        create_vals['partner_id'] = int(partner_id.id)
        create_vals['product_qty'] = int(kw['product_qty'])

        # Create Action
        purchase_request = request.env['purchase.order'].create(create_vals)

        # Create order line for the converted PO
        order_lines = [(5, 0, 0)]
        line_vals = purchase_request.get_order_line_vals(purchase_request.portal_product_id)
        order_lines.append((0, 0, line_vals))
        purchase_request.order_line = order_lines

        return request.redirect('/my/purchase/' + str(purchase_request.id))

    
    @http.route([
        '''/my/purchase/approve/<int:order_id>'''
    ], type='http', auth='public', website=True)
    def approve_purchase_request(self, order_id=None, **kw):

        # Purchase Environment
        Purchase = request.env['purchase.order']

        # Check if the order is in draft portal state
        purchase_obj = Purchase.search([('id', '=', order_id)])
        if purchase_obj.portal_state == "draft":
            purchase_obj.button_approve_rfq()

        return request.redirect('/my/purchase/' + str(order_id))

    
    @http.route([
        '''/my/purchase/reject/<int:order_id>'''
    ], type='http', auth='public', website=True)
    def reject_purchase_request(self, order_id=None, **kw):

        # Purchase Environment
        Purchase = request.env['purchase.order']

        # Check if the order is in draft portal state
        purchase_obj = Purchase.search([('id', '=', order_id)])
        if purchase_obj.portal_state == "draft":
            purchase_obj.button_cancel()

        return request.redirect('/my/purchase/' + str(order_id))

class Home(Home):
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                
                # Check current user group and redirect
                user = request.env.user
                if user.has_group('employee_purchase_portal.group_accounting_team'):
                    return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                else:
                    url = '/my/purchase'
                    return werkzeug.utils.redirect(url)

            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response