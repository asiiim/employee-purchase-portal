from odoo import _, api, fields, models
from odoo.exceptions import UserError

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

    # TODO: Domain the vendor list as per the selected product.
    portal_product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True)
    available_vendor = fields.Many2one('res.partner', string='Available Vendor', 
        change_default=True, 
        tracking=True, 
        domain="[('id', 'in', portal_product_id.seller_ids.ids)]")
    
    # TODO: Override the method "action_convert_to_order"
    """ 
        - Check if the user group is "Accounting Team".
        - Make sure the portal state is "Approved" and change
            the portal_state to "Purchase In Progress".
    """

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


