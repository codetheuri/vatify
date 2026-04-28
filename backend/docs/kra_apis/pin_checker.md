# PIN Checker API (by PIN & by ID)

## Method 1: Check by KRA PIN

**Endpoint (Sandbox):** `POST https://sbx.kra.go.ke/checker/v1/pinbypin`
**Endpoint (Production):** `POST https://api.kra.go.ke/checker/v1/pinbypin`

## Method 2: Check by ID Number

**Endpoint (Sandbox):** `POST https://sbx.kra.go.ke/checker/v1/pinbyid`
**Endpoint (Production):** `POST https://api.kra.go.ke/checker/v1/pinbyid`

## 🔐 Authentication
Use Consumer Key and Secret for the PIN Checker App. Generate token via:
`GET https://sbx.kra.go.ke/v1/token/generate?grant_type=client_credentials`
**Headers:** `Authorization: Basic <Base64(Key:Secret)>`

**App Credentials (Sandbox):**
- Key: `1EMgFiwPlix2OTH1xlygkGhyCEh5hAHeCMy40IbNKYrCtziv`
- Secret: `mdoGb3TqPA5TFlM9OkyKQPNnn7ieKhUSo2bNyfpkc0GMSwGTbmiyPikGtm5PfAvI`

## 🚀 Usage — PIN by PIN

**Body:**
```json
{ "KRAPIN": "P318295670X" }
```

## 🚀 Usage — PIN by ID

**Body:**
```json
{ "ID": "<national_id_or_passport>" }
```

## 🧪 Sample Test Data (Sandbox)

| KRA PIN | Notes |
|---|---|
| `A744610021G` | Individual, Active |
| `A521040203F` | Individual, Active |
| `P318295670X` | Non-Individual (Company), Active |

> 💡 Tip: Use the **My Apps** section in the KRA Developer Portal to get your app credentials.

## ✅ Success Response (PIN by PIN)
```json
{
  "ResponseCode": "23000",
  "Message": "Valid PIN",
  "Status": "OK",
  "PINDATA": {
    "KRAPIN": "P318295670X",
    "TypeOfTaxpayer": "Non Individual",
    "Name": "T. AN 052318TEST NA NA",
    "StatusOfPIN": "Active"
  }
}
```

## ⚠️ Exceptions
- **19005 (NOK):** Invalid PIN
- **19006:** ID Number not found in KRA system

## 💡 Use Case
For validating taxpayer information in the iTax system using KRA PIN or National ID.
Useful for verifying suppliers before claiming input VAT on their invoices.

## 🔗 Our Endpoints
- `POST /v1/tax-periods/validate-pin` → body: `{ "pin": "P318295670X" }`
- `POST /v1/tax-periods/validate-pin-by-id` → body: `{ "id_number": "<id>" }`
