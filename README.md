# ERP Inventory and Order Management — Transactional Reference

I built this project to explore a core enterprise-systems requirement: stock balances, order records and movement journals must remain consistent under partial failures or invalid requests. The reference is a functional **Python + SQLite** implementation; it is not presented as Microsoft Dynamics 365 or an enterprise deployment.

## Run the business workflow

```bash
python erp.py --db out/erp.sqlite3 product SENSOR "Proximity Sensor"
python erp.py --db out/erp.sqlite3 receipt GRN-001 SENSOR 10
python erp.py --db out/erp.sqlite3 sale SO-001 Ada SENSOR 2 12500
python erp.py --db out/erp.sqlite3 report
python -m pip install pytest
python -m pytest -q
```

The unit price argument is **integer cents**. The business rules reject duplicate reference IDs, overselling and negative quantities. Database transactions protect against partial updates.

## Roadmap

A natural extension is to integrate this service with a web API, a role-based approval workflow, purchase orders, invoices and eventually a **documented Microsoft Dynamics 365 connector**, if an authorized tenant becomes available. Until then, it is an independently tested ERP domain-model reference.
