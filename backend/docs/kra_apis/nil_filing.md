# NIL Return Filing API

**Endpoint (Sandbox):** `POST https://sbx.kra.go.ke/dtd/return/v1/nil`

## 🔐 Authentication
Use Consumer Key and Secret for the NIL Return App. Generate token via:
`GET https://sbx.kra.go.ke/v1/token/generate?grant_type=client_credentials`
**Headers:** `Authorization: Basic <Base64(Key:Secret)>`

**App Credentials (Sandbox):**
- Key: `cTCAz7JwGuKM4ZjLm2iNfBTpssBhemr4NBw1bweBQHJuqTMW`
- Secret: `o8seDkhRVzyqzylxSXdlFnPn04k40kktJEGKPGX5qUiqvz1bJT78ToK7HmwctOXY`

## 🚀 Usage
**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

**Body:**
```json
{
  "TAXPAYERDETAILS": {
    "TaxpayerPIN": "A521040203F",
    "ObligationCode": "1",
    "Month": "12",
    "Year": "2016"
  }
}
```

## 🧪 Sample Test Data (Sandbox)

| TaxpayerPIN | ObligationCode | Month | Year |
|---|---|---|---|
| `A521040203F` | `1` | `12` | `2016` |

**ObligationCode Key:**
- `1` = Income Tax Resident Individual
- `2` = Income Tax Resident Non-Individual
- `5` = Value Added Tax (VAT)

## ✅ Success Response
```json
{
  "RESPONSE": {
    "ResponseCode": " 82000",
    "Message": " Successfully Filled NIL Return ",
    "Status": "OK",
    "AckNumber": " KRAKBU1456050925 "
  }
}
```

## ⚠️ Errors
- **82002:** Data Validation Error (wrong PIN, period, or obligation)

## 🔗 Our Endpoint
`POST /v1/tax-periods/file-nil`
```json
{ "user_id": 1, "month": 12, "year": 2016 }
```
