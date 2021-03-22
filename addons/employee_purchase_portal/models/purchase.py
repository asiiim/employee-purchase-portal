# -*- coding: utf-8 -*-

import math
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    
    # Add portal_state for the order
    portal_state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('purchase_in_progress', 'Purchase In Progress'),
        ('ready_to_pick', 'Ready To Pick'),
        ('done', 'Done')
    ], string='Order Portal Status', readonly=True, index=True,
        copy=False, default='draft', tracking=True)

    purchase_maker = fields.Many2one(related='user_id.partner_id', 
        string="Purchase Maker",
        store=True)

    allowed_product_categories = fields.Many2many(related="purchase_maker.allowed_product_categories")

    portal_product_id = fields.Many2one('product.product', 
        string='Product', 
        domain="[('purchase_ok', '=', True), ('categ_id', 'in', allowed_product_categories)]", 
        change_default=True)

    related_product_template = fields.Many2one(related='portal_product_id.product_tmpl_id', 
        string='Product Template', store=True)
    
    supplier_info = fields.Many2one('product.supplierinfo', string='Available Vendor', 
        change_default=True, 
        tracking=True,
        domain="[('product_tmpl_id', '=', related_product_template)]")


    # For now let's assign the vendor field with on_change of supplier_info
    # Need to called the model to set the value from the portal later.
    @api.onchange('supplier_info')
    def on_change_supplier(self):
        self.partner_id = self.supplier_info.name

    
    # Override the method "action_convert_to_order"
    def action_convert_to_order(self):
        """ 
            - Check if the user group is "Accounting Team".
            - Make sure the portal state is "Approved" and change
                the portal_state to "Purchase In Progress".
            - Check the group of the current user.
        """
        # TODO: Create purchase order line

        if self.env.user.has_group('employee_purchase_portal.group_accounting_team'):

            result = super(PurchaseOrder, self).action_convert_to_order()
            self.write({'portal_state': 'purchase_in_progress'})
            return result
        else:
            raise UserError("You are not allowed to make Purchase Order.\nPlease consult the Accounting Team.")

    # TODO: Method to change the portal state to ready to pick
    """
        - Override the method 
        - Change the state to ready to pick 
    """


    # Method to Approve or Reject RFQ by Manager Group Users
    # TODO: Issue: This method is disturbing the method button_confirm()
    def button_approve(self):
        """
            - Make sure this method is accessible to ony Manager group
            - Make sure the portal_state of the RFQ is "Draft"
            - Change the state to "Approve" or "Reject".
        """
        if self.env.user.has_group('employee_purchase_portal.group_purchase_approver') \
            and self.portal_state == "draft":
            self.write({'portal_state': 'approved'})
        else:
            raise UserError("You don't have access to approve the RFQ.")


    # Override cancel action to change the portal state  to "rejected".
    def button_cancel(self):
        if self.env.user.has_group('employee_purchase_portal.group_purchase_approver'):
            result = super(PurchaseOrder, self).button_cancel()
            self.write({
                'portal_state': 'rejected'
            })
        else:
            raise UserError("You don't have access to reject the RFQ.")

    
    # Override the create() method.
    @api.model
    def create(self, vals):
        """
            - Check if the last rejected rfq is older than 30 days.
        """
        orders = self.env['purchase.order'].search([('user_id', '=', self.env.user.id)])
        if orders:
            for order in orders:
                if order.portal_state == 'rejected':
                    
                    order_date = fields.Datetime.from_string(order.date_order)
                    today = fields.Datetime.now()
                    time_delta = today - order_date
                    
                    # No. of day since last rejection from now.
                    rejected_days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400) + 1.0
                    
                    if  rejected_days < 30:
                        raise UserError('Sorry, your last rejected order is still less than a month.')
        return super().create(vals)
    

    # TODO: Make domain to view only self list of order by the employee


