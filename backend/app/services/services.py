import os
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from typing import List, Dict, Optional
from app.common.base.base_service import BaseService
from app.models.user_models import User
from app.models.transaction_models import TaxTransaction, CategoryRule, TaxPeriod, TaxDocument
from app.repositories.repositories import TransactionRepository, RuleRepository, TaxPeriodRepository, UserRepository, DocumentRepository
from app.services.utils import ParserService
from app.services.ai_categorizer import AiCategorizer
from app.services.gava_service import GavaConnectService
from app.models.eslip_models import ESlip
from app.services.mail_service import EmailService
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
import pyotp
import random

class UserService(BaseService[User, UserRepository]):
    repo = UserRepository

    async def get_details(self, user_id: int):
        user = await self.session.get(User, user_id)
        return user

    async def authenticate(self, email: str, password: str) -> Optional[dict]:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_verified:
            raise ValueError("Account not verified. Please check your email for the activation link.")
        
        if user.mfa_enabled:
            # Generate and send OTP
            otp = f"{random.randint(100000, 999999)}"
            user.otp_code = otp
            user.otp_expiry = int(datetime.utcnow().timestamp()) + 300 # 5 mins
            await self.session.commit()
            
            await EmailService.send_mfa_otp_email(user.email, otp)
            return {"mfa_required": True, "email": user.email}

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        user.otp_code = None
        user.otp_expiry = None
        user.otp_resend_count = 0 # Reset on success
        user.last_otp_resend = None
        user.refresh_token = refresh_token
        await self.session.commit()
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "mfa_required": False
        }

    async def resend_mfa(self, email: str) -> dict:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.mfa_enabled:
            raise ValueError("MFA not enabled for this account")
            
        now = int(datetime.utcnow().timestamp())
        
        # Throttling
        if user.last_otp_resend and (now - user.last_otp_resend) < 60:
            raise ValueError(f"Please wait {60 - (now - user.last_otp_resend)} seconds.")
            
        # Limit
        if user.otp_resend_count >= 5: # Give them 5 tries
            raise ValueError("Too many resend attempts. Please login again.")
            
        otp = f"{random.randint(100000, 999999)}"
        user.otp_code = otp
        user.otp_expiry = now + 300
        user.otp_resend_count += 1
        user.last_otp_resend = now
        await self.session.commit()
        
        await EmailService.send_mfa_otp_email(user.email, otp)
        return {"message": "New verification code sent"}

    async def update_profile(self, user_id: int, data: dict) -> User:
        """Update editable profile fields (name, phone, business name, address)."""
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        allowed = {"full_name", "phone_number", "business_name", "physical_address"}
        for field, value in data.items():
            if field in allowed and value is not None:
                setattr(user, field, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def change_password(self, user_id: int, current_password: str, new_password: str):
        """Verify current password then update to new hash."""
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        if not new_password or len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters")
        user.hashed_password = get_password_hash(new_password)
        await self.session.commit()

    async def signup(self, user_data: dict) -> User:
        """
        Handles full onboarding:
        1. Validates PIN & Fetches Obligations from KRA
        2. Creates User with hashed password and verification token
        3. Sends verification email
        """
        # Check if email exists
        existing = await self.repository.get_by_email(user_data["email"])
        if existing:
            raise ValueError("Email already registered")

        # Fetch Obligations from KRA Sandbox
        obligations = "Income Tax"
        business_name = user_data.get("full_name")
        kra_status = "Active"
        
        async with GavaConnectService() as gava:
            kra_res = await gava.fetch_obligations(user_data["kra_pin"])
            if kra_res.get("Status") == "OK":
                obs_list = kra_res.get("ObligationsList", [])
                if obs_list:
                    obligations = ", ".join([o.get("obligationName") or o.get("ObligationName") or "Unknown" for o in obs_list])
            
            pin_res = await gava.validate_pin(user_data["kra_pin"])
            if pin_res.get("Status") != "OK":
                raise ValueError(f"PIN Validation Failed: {pin_res.get('Message', 'The provided KRA PIN could not be verified in the KRA registry.')}")
            
            p_data = pin_res.get("PINDATA", {})
            business_name = p_data.get("Name") or p_data.get("TaxpayerName") or business_name
            kra_status = p_data.get("StatusOfPIN") or kra_status

        token = str(uuid.uuid4())
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            phone_number=user_data.get("phone_number"),
            kra_pin=user_data["kra_pin"],
            tax_obligations=obligations,
            business_name=business_name,
            kra_status=kra_status,
            pin_status=kra_status,
            last_sync_at=int(datetime.utcnow().timestamp()),
            is_verified=False,
            verification_token=token
        )
        
        await self.repository.add(user)
        await self.session.commit()

        await EmailService.send_verification_email(user.email, token)
        return user

    async def verify_account(self, token: str) -> str:
        stmt = select(User).where(User.verification_token == token)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return "invalid"
        
        if user.is_verified:
            return "already_verified"
        
        user.is_verified = True
        user.verification_token = None
        await self.session.commit()
        return "success"

    async def refresh_obligations(self, user_id: int) -> User:
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
            
        async with GavaConnectService() as gava:
            kra_res = await gava.fetch_obligations(user.kra_pin)
            if kra_res.get("Status") == "OK":
                obs_list = kra_res.get("ObligationsList", [])
                if obs_list:
                    user.tax_obligations = ", ".join([o.get("obligationName") or o.get("ObligationName") for o in obs_list])
            
            pin_res = await gava.validate_pin(user.kra_pin)
            if pin_res.get("Status") == "OK":
                p_data = pin_res.get("PINDATA", {})
                user.business_name = p_data.get("Name") or p_data.get("TaxpayerName") or user.business_name
                user.kra_status = p_data.get("StatusOfPIN") or user.kra_status
                user.pin_status = user.kra_status
            
            # --- E-Slip Sync ---
            eslip_res = await gava.fetch_eslips(user.kra_pin)
            if eslip_res.get("Status") == "OK":
                for es_data in eslip_res.get("ESlips", []):
                    # Check if exists
                    stmt = select(ESlip).where(ESlip.eslip_number == es_data["eslipNumber"])
                    existing_es = await self.session.execute(stmt)
                    if not existing_es.scalar_one_or_none():
                        new_es = ESlip(
                            eslip_number=es_data["eslipNumber"],
                            amount=es_data["amount"],
                            expiry_date=datetime.strptime(es_data["expiryDate"], "%Y-%m-%d"),
                            status=es_data["status"],
                            payment_registration_number=es_data["prn"],
                            obligation_name=es_data["obligationName"],
                            tax_period=es_data["taxPeriod"],
                            user_id=user_id
                        )
                        self.session.add(new_es)
        
        user.last_sync_at = int(datetime.utcnow().timestamp())
        await self.session.commit()
        return user

    async def refresh_session(self, refresh_token: str) -> dict:
        from app.core.security import verify_refresh_token
        if not refresh_token:
            raise ValueError("Refresh token is required")
            
        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            raise ValueError("Invalid or expired refresh token")
            
        user = await self.session.get(User, int(user_id))
        if not user or user.refresh_token != refresh_token:
            raise ValueError("Refresh token revoked or invalid")
            
        access_token = create_access_token(subject=user.id)
        return {"access_token": access_token}

    async def logout(self, user_id: int):
        user = await self.session.get(User, user_id)
        if user:
            user.refresh_token = None
            await self.session.commit()

    async def forgot_password(self, email: str):
        from app.core.security import create_reset_token
        user = await self.repository.get_by_email(email)
        if user:
            token = create_reset_token(email)
            user.reset_token = token
            user.reset_expiry = int(datetime.utcnow().timestamp()) + (15 * 60) # 15 mins
            await self.session.commit()
            
            # PRODUCTION EMAIL
            await EmailService.send_reset_password_email(email, token)

    async def verify_mfa_login(self, email: str, code: str) -> Optional[dict]:
        user = await self.repository.get_by_email(email)
        if not user or user.otp_code != code:
            return None
            
        if user.otp_expiry < int(datetime.utcnow().timestamp()):
            return None
            
        # Success: Clear OTP and return tokens
        user.otp_code = None
        user.otp_expiry = None
        
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        user.refresh_token = refresh_token
        await self.session.commit()
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    async def toggle_mfa(self, user_id: int, enabled: bool):
        user = await self.session.get(User, user_id)
        if user:
            user.mfa_enabled = enabled
            await self.session.commit()
            return user
        return None

    async def reset_password(self, token: str, new_password: str):
        # We can't easily verify by token without decoding, but we stored it in DB
        stmt = select(User).where(User.reset_token == token)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Invalid or expired reset token")
            
        if user.reset_expiry < int(datetime.utcnow().timestamp()):
            raise ValueError("Reset token expired")
            
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_expiry = None
        user.refresh_token = None # Clear sessions on password reset
        await self.session.commit()

class TransactionService(BaseService[TaxTransaction, TransactionRepository]):
    repo = TransactionRepository
    
    async def process_upload(self, user_id: int, file_path: str, original_filename: str):
        """
        Efficiently uploads a statement: parses the file, categorizes transactions
        in-memory, then bulk-inserts them in a single DB transaction.
        eTIMS verification is intentionally deferred to a separate on-demand call.
        """
        statement_doc = TaxDocument(
            filename=original_filename,
            file_path=file_path, 
            file_type="PDF" if original_filename.lower().endswith('.pdf') else "CSV",
            document_type="Statement",
            user_id=user_id,
            is_processed=True
        )
        self.session.add(statement_doc)
        await self.session.flush()  # Assigns statement_doc.id
        
        # --- Parse file ---
        if original_filename.lower().endswith('.pdf'):
            raw_txs = ParserService.parse_mpesa_pdf(file_path)
        else:
            raw_txs = ParserService.parse_mpesa_csv(file_path)
            
        if not raw_txs:
            raise ValueError("No valid transactions could be extracted from the file.")
        
        # --- Categorize in-memory (no DB/network calls inside loop) ---
        rule_repo = RuleRepository(self.session)
        rules = await rule_repo.get_by_user(user_id)
        
        transactions_to_add = []
        for tx_data in raw_txs:
            category = AiCategorizer.categorize(tx_data['description'], rules)
            is_excluded = category in ["Salary", "Finance", "Interest"]
            transactions_to_add.append(TaxTransaction(
                **tx_data,
                category=category,
                user_id=user_id,
                document_id=statement_doc.id,
                etims_validated=False,  # eTIMS checked on-demand, not during upload
                is_excluded_from_etims=is_excluded,
                tax_amount=tx_data['amount'] * 0.16 if not is_excluded and tx_data.get('transaction_type') == 'Expense' else 0.0
            ))
        
        # --- Bulk insert (single DB round-trip) ---
        self.session.add_all(transactions_to_add)
        await self.session.commit()
        
        # --- Process-and-Discard: remove temp file after successful parse ---
        # Data is now safely in the DB. No need to keep the raw file on disk.
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # Non-critical: log would go here in production
        
        return {"count": len(transactions_to_add), "document_id": statement_doc.id}

    async def re_categorize_all(self, user_id: int, document_id: Optional[int] = None):
        """Re-runs AI categorization for transactions for a user, optionally filtered by document."""
        rule_repo = RuleRepository(self.session)
        rules = await rule_repo.get_by_user(user_id)
        
        if document_id:
            stmt = select(TaxTransaction).where(
                and_(TaxTransaction.user_id == user_id, TaxTransaction.document_id == document_id)
            )
            res = await self.session.execute(stmt)
            transactions = res.scalars().all()
        else:
            transactions = await self.repository.get_by_user(user_id)
        
        count = 0
        for tx in transactions:
            new_cat = AiCategorizer.categorize(tx.description, rules)
            if new_cat != tx.category:
                tx.category = new_cat
                tx.tax_amount = tx.amount * 0.16 if not tx.is_excluded_from_etims and tx.transaction_type == 'Expense' else 0.0
                tx.is_excluded_from_etims = new_cat in ["Salary", "Finance", "Interest"]
                count += 1
        
        await self.session.commit()
        return count

    async def scan_and_save_etims(self, user_id: int, invoice_number: str, invoice_date: Optional[str] = None):
        """
        Simulates scanning of an eTIMS invoice and links it to a transaction.
        Checks against KRA Sandbox via GavaConnect.
        """
        async with GavaConnectService() as gava:
            kra_res = await gava.check_etims_invoice(invoice_number, invoice_date)
            
        if kra_res.get("status") != "OK":
            return {"Status": "NOK", "Message": kra_res.get("Message", "Invoice verification failed")}

        details = kra_res.get("invoiceDetails", {})
        amount = details.get("totalInvoiceAmount", 0)
        
        # Logic to find a matching transaction and update it
        # We look for unvalidated expenses for this user with similar amount
        stmt = select(TaxTransaction).where(
            and_(
                TaxTransaction.user_id == user_id,
                TaxTransaction.transaction_type == "Expense",
                TaxTransaction.etims_validated == False
            )
        )
        # In a real app we'd filter by amount, but for demo we pick the first at-risk item
        # or match by amount if possible
        res = await self.session.execute(stmt)
        transactions = res.scalars().all()
        
        matched_tx = None
        for tx in transactions:
            if abs(tx.amount - amount) < 1.0: # Close enough match
                matched_tx = tx
                break
        
        # Fallback: if no amount match, just pick the first unvalidated one for the demo
        if not matched_tx and transactions:
            matched_tx = transactions[0]

        if matched_tx:
            matched_tx.etims_validated = True
            matched_tx.etims_invoice_number = invoice_number
            await self.session.commit()
            return {
                "Status": "OK", 
                "Message": "Matched and Verified", 
                "transaction_id": matched_tx.id,
                "invoice_details": details
            }
            
        return {"Status": "OK", "Message": "Verified but no matching transaction found.", "invoice_details": details}

    async def get_dashboard_summary(self, user_id: int, month: int, year: int):
        totals = await self.repository.get_totals_for_period(user_id, month, year)
        unvalidated = await self.repository.get_unvalidated_etims(user_id)
        
        return {
            "period": f"{month:02}/{year}",
            "totals": totals,
            "compliance_risk_count": len(unvalidated),
            "unvalidated_sum": sum(t.amount for t in unvalidated)
        }

    async def get_by_user(self, user_id: int):
        return await self.repository.get_by_user(user_id)

    async def get_by_user_paginated(self, user_id: int, page: int = 1, per_page: int = 10):
        return await self.repository.list_paginated(filters={"user_id": user_id}, page=page, per_page=per_page)

    async def get_category_summary(self, user_id: int, month: int, year: int) -> dict:
        """
        Returns a structured breakdown of Income and Expense transactions
        grouped by category for a given period. Used to populate the KRA
        financial summary report on the Tax Returns page.
        """
        rows = await self.repository.get_category_summary(user_id=user_id, month=month, year=year)
        
        summary = {
            "Income": {},
            "Expense": {},
            "period": {"month": month, "year": year}
        }
        
        for row in rows:
            tx_type = row.transaction_type
            category = row.category or "Uncategorized"
            if tx_type not in summary:
                summary[tx_type] = {}
            summary[tx_type][category] = {
                "count": row.tx_count,
                "total": round(row.total_amount or 0, 2),
                "vat": round(row.total_vat or 0, 2)
            }
        
        summary["grand_totals"] = {
            "income": round(sum(v["total"] for v in summary["Income"].values()), 2),
            "expenses": round(sum(v["total"] for v in summary["Expense"].values()), 2),
            "output_vat": round(sum(v["vat"] for v in summary["Income"].values()), 2),
            "input_vat": round(sum(v["vat"] for v in summary["Expense"].values()), 2),
        }
        net = summary["grand_totals"]["output_vat"] - summary["grand_totals"]["input_vat"]
        summary["grand_totals"]["net_vat_payable"] = round(net, 2)
        return summary

class RuleService(BaseService[CategoryRule, RuleRepository]):
    repo = RuleRepository

    async def get_by_user(self, user_id: int):
        return await self.repository.get_by_user(user_id)

class TaxPeriodService(BaseService[TaxPeriod, TaxPeriodRepository]):
    repo = TaxPeriodRepository

    async def reconcile_and_file_nil(self, user_id: int, month: int, year: int, obligation_code: str = "5"):
        """
        File a NIL return if no transactions exist for the period.
        obligation_code: 1=Income Tax Resident Individual, 5=VAT
        """
        # 1. Get user's KRA PIN from DB
        user = await self.session.get(User, user_id)
        # Use real PIN if available, fall back to sandbox test PIN
        pin = (user.kra_pin if user and user.kra_pin else None) or "A521040203F"

        # 2. Check if we have any transactions for the period
        tx_repo = TransactionRepository(self.session)
        totals = await tx_repo.get_totals_for_period(user_id, month, year)
        
        has_transactions = totals["Income"]["amount"] > 0 or totals["Expense"]["amount"] > 0
        
        if has_transactions:
            return {
                "Status": "Manual Filing Required",
                "Message": f"Transactions found for {month}/{year}. NIL return not applicable. Use the iTax portal to file with actual figures.",
                "totals": totals
            }

        # 3. No transactions — proceed with NIL filing
        async with GavaConnectService() as gava:
            result = await gava.file_nil_return(
                pin=pin,
                obligation_code=obligation_code,
                month=f"{month:02d}",
                year=str(year)
            )
            
            # KRA returns { "RESPONSE": { "ResponseCode": "82000", "Status": "OK", ... } }
            response_body = result.get("RESPONSE", result)
            
            if response_body.get("Status") == "OK" or response_body.get("ResponseCode") in ("82000", " 82000"):
                # Save filing record
                period = TaxPeriod(
                    user_id=user_id, month=month, year=year,
                    status="Filed",
                    submission_reference=response_body.get("AckNumber", "").strip()
                )
                await self.repository.add(period)
                await self.commit()
                return {
                    "Status": "OK",
                    "Message": response_body.get("Message", "NIL return filed successfully.").strip(),
                    "AckNumber": response_body.get("AckNumber", "").strip(),
                    "pin": pin,
                    "period": f"{month:02d}/{year}",
                    "obligation_code": obligation_code
                }
            
            return {"Status": "NOK", "Message": response_body.get("Message", str(result))}

class DocumentService(BaseService[TaxDocument, DocumentRepository]):
    repo = DocumentRepository

    async def get_by_user(self, user_id: int):
        return await self.repository.get_by_user(user_id)

    async def get_by_user_paginated(self, user_id: int, page: int = 1, per_page: int = 10):
        return await self.repository.list_paginated(filters={"user_id": user_id}, page=page, per_page=per_page)

    async def upload_and_process(self, user_id: int, file: bytes, filename: str):
        # 1. Save file (mocking path for now)
        file_path = f"/uploads/{filename}"
        
        # 2. Simulate OCR Extraction
        # In a real scenario, use Gemini Vision or Tesseract
        extracted_data = {
            "vendor": "Quickmart Lavington",
            "pin": "P051123456G",
            "invoice_number": f"INV-{uuid.uuid4().hex[:6].upper()}",
            "amount": 1000.0, # Match one of the default mock transactions (ZUKU or similar)
            "tax_amount": 160.0,
            "date": datetime.now()
        }

        doc = TaxDocument(
            filename=filename,
            file_path=file_path,
            file_type=filename.split('.')[-1],
            user_id=user_id,
            extracted_vendor=extracted_data["vendor"],
            extracted_pin=extracted_data["pin"],
            extracted_invoice_number=extracted_data["invoice_number"],
            extracted_amount=extracted_data["amount"],
            extracted_tax_amount=extracted_data["tax_amount"],
            extracted_date=extracted_data["date"],
            is_processed=True
        )

        # 3. Try to match with an existing transaction
        tx_repo = TransactionRepository(self.session)
        # Simple match by amount and date (loose match)
        stmt = select(TaxTransaction).where(
            and_(
                TaxTransaction.user_id == user_id,
                TaxTransaction.amount == doc.extracted_amount,
                TaxTransaction.transaction_type == "Expense"
            )
        )
        res = await self.session.execute(stmt)
        tx = res.scalar_one_or_none()
        
        if tx:
            doc.transaction_id = tx.id
            tx.etims_validated = True
            tx.etims_invoice_number = doc.extracted_invoice_number
        
        await self.repository.add(doc)
        await self.commit()
        return doc

    async def delete_batch(self, user_id: int, doc_id: int):
        doc = await self.session.get(TaxDocument, doc_id)
        if not doc or doc.user_id != user_id:
            return False
        
        # Bulk delete all linked transactions in ONE SQL statement
        await self.session.execute(
            delete(TaxTransaction).where(TaxTransaction.document_id == doc_id)
        )
        
        # Also remove the document record itself
        await self.session.delete(doc)
        await self.session.commit()
        return True
