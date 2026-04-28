# Fetch Taxpayer Obligations API

**Endpoint (Sandbox):** `POST https://sbx.kra.go.ke/dtd/checker/v1/obligation`

## 🔐 Authentication
Use Consumer Key and Secret for the Obligations App. Generate token via:
`GET https://sbx.kra.go.ke/v1/token/generate?grant_type=client_credentials`
**Headers:** `Authorization: Basic <Base64(Key:Secret)>`

**App Credentials (Sandbox):**
- Key: `My1Kd4eGIAC2vBIBLRXyfF6lGQE84cdZvYejLxEinNfhBTYf`
- Secret: `x1GIrZa1kmTK3hu8QIfzXaFAahvjTMkNgfVdMMpLbhYvsEuUhBFLkJKgdCmywEmf`

## 🚀 Usage
**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

**Body:**
```json
{ "taxPayerPin": "A744610021G" }
```

## 🧪 Sample Test Data (Sandbox)

| KRA PIN | Type |
|---|---|
| `A744610021G` | Individual |
| `A948312567Q` | Individual |
| `A521040203F` | Individual |
| `P318295670X` | Non-Individual |
| `P531107121Z` | Non-Individual |
| `P915347031J` | Non-Individual |
| `A553210740V` | Individual |

## ✅ Success Response
```json
{
  "ResponseCode": "20000",
  "ResponseMsg": "Valid KRA Pin",
  "Status": "OK",
  "ObligationsList": [
    { "obligationId": "2", "obligationName": "Income Tax - Resident Individual", "obligationType": "NRM" },
    { "obligationId": "5", "obligationName": "VAT", "obligationType": "NRM" }
  ]
}
```

## ⚠️ Exceptions
- **20001 (NOK):** Invalid KRA Pin

## 💡 Use Cases
- Automated Reminders & Notifications for filling obligations in ERP systems
- Verifying which tax types a PIN is registered for before filing

## 🔗 Our Endpoint
`GET /v1/tax-periods/obligations?pin=A744610021G`
