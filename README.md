# Employee Purchase Portal
------------------------------------------------------------------------------------------------------
This module helps employees to buy some products offering discounts and better prices. When an employee needs to buy something, he/she can create and order for this product and select from which vendor he/she wants to buy. The order has to be approved by the manager and the product is purchased from that vendor. Once the product is sent to the company, the employee can pick it up at the office. It is also possible that the Manager rejects the order, based on the company’s decision. In that case, the employee can create a new order only the next month (it can be for the same product or for a different product). For employees and managers, we want to handle this logic using portals, and only give backend access to our accounting team to confirm the sales, purchases, invoices, etc.

# Steps to use the module
1. Create Database
	Create a fresh database with the name of you choice.
	Master password: rx8d-s4j5-z2zw

2. Install Module
	Install the module “employee_purchase_portal”
	Create any three users as shown below:

3. Allocate Groups Access
	Provide group access to the user.

	If you are creating an employee user, provide Purchase/User and Purchase Portal/Purchase Maker groups access.
	If you are creating a manager user, provide Purchase/User and Purchase Portal/Purchase Approver groups access.
	If you are creating an accounting team user, provide Purchase/Administrator and Purchase Portal/Accounting Team groups access.
4. Setup Products and Tax
	Create the products with categories which are buyable by employees.
	Add the suppliers with the price for that product.

	Now, goto Contacts > Employee Name

	Go to that form view and select the product categories which are allowed to be bought by that employee.


5. Create Purchase Request by Employee
	Login with the employee user credentials

	Then the employee portal is loaded.

	Create Purchase Request by clicking the “Create Request” button. Then, form view loaded as follows.

6. Approve/Reject Purchase Request
	Login with manager user credential and it will land at manager portal.
	Go to the draft order request form view of any order.

	Simply click any one of the buttons to “Approve” or “Reject” that order.

7. Accounting Team Process the Order
	Login with accounting team user credentials.
	Go to Purchase > Select any one approved RFQ (Request for Quotation)
	Click on “Convert to Order”.

	New Purchase Order is created from that RFQ.

8. Make Ready to Pick Up
	As soon as the product is received by the Accounting Team, the user clicks on the button to notify the employee to pick up the delivery.

9. Change to state Done
	Soon after the employee picks up the product, the accounting team user clicks the button in that order to set it to Done.


