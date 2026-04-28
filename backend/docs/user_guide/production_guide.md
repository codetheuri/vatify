# Moving to Production Guide

To move TaxAgent from the Sandbox to the Real KRA Production environment, follow these steps:

## 1. KRA Portal Actions
1. **Apply for Go Live**: Log in to the KRA Developer Portal and click the "Initiate Go Live" button for each of your 4 products (`PIN Checker`, `Invoice Checker`, `NIL Return`, `Taxpayer Obligations`).
2. **Approval**: Wait for KRA to approve your production credentials.
3. **Copy Production Keys**: Once approved, you will get a new set of **Consumer Keys** and **Secrets** specifically for Production.

## 2. Configuration Changes
Open your `.env` file and update the following:

```bash
# 🟢 CHANGE THIS: Update Base URL to Production
GAVA_CONNECT_BASE_URL=https://api.kra.go.ke

# 🟢 CHANGE THESE: Swap your Sandbox keys with Production keys
KRA_PIN_VALIDATION_KEY=PROD_KEY_...
KRA_PIN_VALIDATION_SECRET=PROD_SECRET_...
# ... (Repeat for all 4 apps)
```

## 3. Important Notes
* **Real Data**: In Production, calls to `file_nil_return` will actually file a legal return with KRA. **Do not test this with dummy data.**
* **PINs**: Real PINs (like yours: A019914707A) will now work perfectly.
* **Compliance**: Always ensure your local database matches KRA records before triggering any submission.
