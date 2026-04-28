# Data & Document Requirements

Vatify is a **Reconciliation Assistant**. Its primary job is to ensure that your financial activity matches your tax reporting.

## 📥 What to Upload

### 1. Money Movement (The "Statement")
Current support: **M-Pesa Business Statements (CSV)**.
*   **Why?** This is the ultimate proof of income and expenses. KRA looks at bank/mobile money statements during audits.
*   **Format**: Export your statement from the M-Pesa portal/app as a CSV file.

### 2. Transaction Records
While Statements show the *money*, the following details should be extracted or matched:
*   **Receipt Numbers / Receipt IDs**: Used to verify against eTIMS.
*   **Transaction Descriptions**: Used by our AI to categorize the tax (e.g., "Electricity" -> Utilities, "Stock" -> Raw Materials).

## 📄 Supporting (Physical) Documents
Users do not need to upload images of these documents *yet*, but they should keep them for audits:
1. **eTIMS Invoices**: When you pay a supplier, ensure you receive an eTIMS invoice. Our app will use the **Receipt Number** from your M-Pesa statement to check if KRA has that invoice on file.
2. **Delivery Notes / ETR Receipts**: For cash transactions that don't appear on M-Pesa.
3. **Credit/Debit Notes**: If a transaction was reversed or a refund was issued.

## ⚡ What Happens After Upload? (The Result)

Once the app has both your **Statements** and **Invoice Data**, it performs three critical tasks:

### 1. Tax Deductibility Verification
The system compares your spending against KRA's database. If a transaction (e.g., KES 10,000 for supplies) is matched to a verified eTIMS invoice, it is marked as **"Audit-Proof."** If not, the app warns you that this expense will be rejected by KRA during an audit.

### 2. VAT Offset Calculation
For VAT-obligated users, the app automatically calculates your **Input VAT** from verified invoices. This tells you exactly how much tax you can save this month by offsetting what you paid to suppliers against what you collected from customers.

### 3. Automated NIL Filing Trigger
If the app analyzes a month and finds **zero income** and **zero expenses** (or only non-taxable personal transfers), it will offer to **automatically file your NIL return** using the credentials you provided, saving you the manual log-in process.

### 4. Direct Compliance Score
You get a "health bar" for your business. 
*   **100%**: Every penny spent is backed by a KRA-verified invoice.
*   **<50%**: High risk. You are spending money on suppliers who aren't reporting it, meaning you are overpaying your taxes.
