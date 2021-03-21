from odoo import _, api, fields, models
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

# -*- coding: utf-8 -*-

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

    # Boolean field to store the rejected RFQ
    rejected_rfq = fields.Boolean("Rejected", copy=False, default=False)

    # Domain the vendor list as per the selected product.
    portal_product_id = fields.Many2one('product.product', string='Product', 
        domain=[('purchase_ok', '=', True)], change_default=True)
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
    
    # TODO: Override the method "action_convert_to_order"
    def action_convert_to_order(self):
        """ 
            - Check if the user group is "Accounting Team".
            - Make sure the portal state is "Approved" and change
                the portal_state to "Purchase In Progress".
            - Check the group of the current user.
        """
        accounting_team_group_ref = \
            self.env.ref('employee_purchase_portal.group_accounting_team')

        if self.env.user.has_group(ccounting_team_group_ref):

            result = super(PurchaseOrder, self).action_convert_to_order()

    # TODO: Method to Approve or Reject RFQ by Manager Group Users
    """
        - Make sure this method is accessible to ony Manager group
        - Make sure the portal_state of the RFQ is "Draft"
        - Change the state to "Approve" or "Reject".
        - Set the field "rejected_rfq" to True.
    """

    # TODO: Override the create() method.
    """
        - Check if the last rejected rfq is older than 30 days.
        - Check that users of the group "Manager" & "Acc Team" cannot create RFQ
    """

    # TODO: Make domain to view only self list of order


