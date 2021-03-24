# -*- coding: utf-8 -*-

import base64
from collections import OrderedDict

from odoo import http, _
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
from odoo.addons.portal.controllers.portal import \
    pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Binary
from odoo.tools import image_process

import logging
_logger = logging.getLogger(__name__)

import requests
from odoo.exceptions import ValidationError

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
            order_sudo = self._document_check_access('purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._purchase_order_get_page_view_values(order_sudo, access_token, **kw)
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id
        return request.render("purchase.portal_my_purchase_order", values)