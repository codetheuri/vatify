# Vatify — KRA Compliance Simplified

**Vatify** is a full-stack SaaS platform that helps Kenyan SMEs automate VAT compliance, reconcile M-Pesa statements against KRA eTIMS records, and file tax returns — all in one place.

---

## 🗂 Project Structure

```
vatify/
├── backend/    # FastAPI + SQLite REST API
└── frontend/   # Nuxt 4 (Vue 3) web application
```

---

## 🚀 Getting Started

### Backend (FastAPI)

```bash
cd backend

# Install dependencies
poetry install

# Copy and configure environment
cp .env.example .env

# Start the development server
poetry run uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### Frontend (Nuxt 4)

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
# → http://localhost:3000
```

---

## ⚙️ Environment Variables

Create `backend/.env` from the template below:

```env
DATABASE_URL=sqlite+aiosqlite:///./vatify.db
SECRET_KEY=change_me_to_a_long_random_string

# KRA Sandbox
GAVA_CONNECT_BASE_URL=https://sbx.kra.go.ke
KRA_PIN_VALIDATION_KEY=
KRA_PIN_VALIDATION_SECRET=
KRA_INVOICE_CHECKER_KEY=
KRA_INVOICE_CHECKER_SECRET=
KRA_NIL_FILING_KEY=
KRA_NIL_FILING_SECRET=
KRA_OBLIGATIONS_KEY=
KRA_OBLIGATIONS_SECRET=

# SMTP (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your@gmail.com
SMTP_FROM_NAME=Vatify
```

---

## ✨ Features

| Feature | Status |
|---|---|
| KRA PIN validation on signup | ✅ |
| Email verification (account activation) | ✅ |
| JWT auth with refresh tokens | ✅ |
| Multi-Factor Authentication (OTP via email) | ✅ |
| MFA resend with rate limiting | ✅ |
| KRA obligations sync (Sandbox) | ✅ |
| M-Pesa statement parsing & categorisation | ✅ |
| E-Slip history | ✅ |
| Tax returns management | ✅ |
| NIL return filing | ✅ |
| Profile + password management | ✅ |
| Password reset via email | ✅ |

---

## 🛡 Security Notes

- Passwords are hashed with `bcrypt_sha256`
- JWT tokens use RS256 / HS256 via `python-jose`
- `.env` is **never committed** — add your own from the template above
- KRA API credentials are sandbox-only in this repo

---

## 📄 License

MIT
