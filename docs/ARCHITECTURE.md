# ERP process and data model

## Business flows

1. **Item master**: define a unique SKU and a product name.
2. **Goods receipt**: record a receipt reference and increment stock in the same database transaction.
3. **Sales order**: validate stock, create the order, create an inventory movement and decrement stock atomically.
4. **Audit**: compare the inventory balance to movement deltas.

The `movement` table is an immutable journal keyed by reference to protect against accidental double posting. Pricing is stored in integer cents. An order is one line in this reference; multiple lines, tax rules, procurement approvals, financial ledger postings, RBAC, UI and integrations with Microsoft Dynamics 365 remain outside the implementation.

## Safety

No Microsoft tenant, customer records, finance credentials or production ERP services are used. This project is independently written reference logic, not a proprietary Microsoft Dynamics clone.
