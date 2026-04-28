# Invoice Checker API

**Endpoint (Sandbox):** `POST https://sbx.kra.go.ke/checker/v1/invoice`

## 🔐 Authentication
Use Consumer Key and Secret for the Invoice Checker App. Generate token via:
`GET https://sbx.kra.go.ke/v1/token/generate?grant_type=client_credentials`
**Headers:** `Authorization: Basic <Base64(Key:Secret)>`

**App Credentials (Sandbox):**
- Key: `2DErf98kWGrBVtppEGFIFs6fOGNKzbNUOuDWmGer703j8Qx3`
- Secret: `wgtqgafNME8ue720IrZbRrwjcY8kWGrPqX3mFeBKRJkyUrmM8IQIlJ1EAPnNwfCm`

## 🚀 Usage
**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

**Body:**
```json
{
  "invoiceNumber":"KRACU0100058659/5134",
  "invoiceDate":"2024-08-18"
}
```

## 🧪 Sample Test Data (Sandbox)

| invoiceNumber | invoiceDate |
|---|---|
| `KRACU0100058659/5134` | `2024-08-18` |
| `KRACU0300001191/90697` | `2020-06-13` |

## ✅ Success Response
```json
{
  "responseCode": 40000,
  "responseDesc": "Invoice details retrieved successfully.",
  "status": "OK",
  "invoiceDetails": {
    "salesDate": "2025-10-26",
    "totalInvoiceAmount": 1764.0,
    "totalTaxAmount": 243.31,
    "supplierName": "Avas Limit"
  }
}
```

## ⚠️ Error Codes
- **40001:** Invoice not found
- **40005:** Unable to process request
- **50000:** Internal server error

## 🔗 Our Endpoint
`POST /v1/tax-periods/check-invoice`
```json
{ "invoice_number": "KRACU0100058659/5134", "invoice_date": "2024-08-18" }
```
