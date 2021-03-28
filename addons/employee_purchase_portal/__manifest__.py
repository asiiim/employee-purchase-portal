# -*- coding: utf-8 -*-
{
    'name' : 'Employee Purchase Portal',
    'version' : '13.0.0.1',
    'summary': 'Purchase portal for the employee and the manager.',
    'sequence': 1,
    'description': """
        Employee Purchase Portal
        ==========================
        This module builds the portal for the employee and the manager to fulfill the worflow
        of the purchase process. Moreover, there are internal users who actually process the 
        purchase if verified by the manager through the portal.
    """,
    'category': 'Purchase',
    'author': 'Aashim Bajracharya',
    'email': 'ashimbazracharya@gmail.com',
    'depends' : ['purchase_isolated_rfq', 'portal', 'product', 'web', 'contacts'],
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/purchase.xml',
        'views/res_partner.xml',
        'views/purchase_portal_render.xml'
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
