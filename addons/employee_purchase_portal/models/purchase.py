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
    ], string='Order Portal Status', readonly=True, index=True, \ 
        copy=False, default='draft', tracking=True)

    # Boolean field to store the rejected RFQ
    rejected_rfq = fields.Boolean("Rejected", copy=False, default=False)

    # TODO: Override the method "action_convert_to_order"
    """ 
        - Check if the user group is "Accounting Team".
        - Make sure the portal state is "Approved" and change
            the portal_state to "Purchase In Progress".
    """
        
    # TODO: Check that users of the group "Manager" & "Acc Team" cannot create RFQ
    """    
        - Check the create() method with the above mentioned
            group to be forbiddedn to create the RFQ.
    """

    # TODO: Domain the vendor list as per the selected product.

    # TODO: Override the create() method.
    """
        - Check if the last rejected rfq is older than 30 days.
    """

    # TODO: Make domain to view only self list of order


