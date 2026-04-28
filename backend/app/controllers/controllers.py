import os
import shutil
import uuid
from typing import Optional
from fastapi import Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.common.base_controller import BaseController, route
from app.core.db import get_db
from app.services.services import TransactionService, RuleService, TaxPeriodService, UserService, DocumentService
from app.services.exporter import ExporterService
from app.core.security import create_access_token, get_current_user
from app.models.user_models import User
from app.models.user_schemas import UserCreate, UserLogin, UserVerify

class DocumentController(BaseController):
    module = "documents"
    tags = ["Documents"]

    @route("post", "/upload")
    async def upload_document(self, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = DocumentService(db)
        content = await file.read()
        doc = await service.upload_and_process(user_id=current_user.id, file=content, filename=file.filename)
        return self.payload_response(data=doc, message="Document uploaded and processed.")

    @route("get", "/")
    async def list_documents(self, page: int = 1, per_page: int = 10, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = DocumentService(db)
        items, total = await service.get_by_user_paginated(user_id=current_user.id, page=page, per_page=per_page)
        
        pagination = {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "path": "/v1/documents/"
        }
        return self.payload_response(data=items, one_record=False, pagination=pagination)
    @route("delete", "/{doc_id}")
    async def delete_document(self, doc_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = DocumentService(db)
        success = await service.delete_batch(user_id=current_user.id, doc_id=doc_id)
        if not success:
            return self.error_response("Failed to delete or document not found", status_code=400)
        return self.payload_response(data={}, message="Document and associated records removed.")

class UserController(BaseController):
    module = "users"
    tags = ["Users"]

    @route("get", "/me")
    async def get_me(self, current_user: User = Depends(get_current_user)):
        return self.payload_response(data=current_user)

    @route("post", "/update-profile")
    async def update_profile(self, data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        try:
            updated = await service.update_profile(current_user.id, data)
            from app.models.user_schemas import UserResponse
            return self.payload_response(data=UserResponse.model_validate(updated))
        except ValueError as e:
            return self.error_response(str(e), status_code=400)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Update profile error: {e}")
            return self.error_response("Failed to update profile", status_code=500)

    @route("post", "/change-password")
    async def change_password(self, data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        try:
            await service.change_password(current_user.id, data.get("current_password"), data.get("new_password"))
            return self.payload_response(data={}, message="Password changed successfully.")
        except ValueError as e:
            return self.error_response(str(e), status_code=400)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Change password error: {e}")
            return self.error_response("Failed to change password", status_code=500)

    @route("post", "/refresh-obligations")
    async def refresh_obligations(self, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        try:
            user = await service.refresh_obligations(current_user.id)
            return self.payload_response(data=user, message="KRA obligations refreshed successfully.")
        except ValueError as e:
            return self.error_response(str(e), status_code=400)

    @route("get", "/{user_id}")
    async def get_user(self, user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        user = await service.get_details(user_id)
        if not user:
            return self.error_response("User not found", status_code=404)
        from app.models.user_schemas import UserResponse
        return self.payload_response(data=UserResponse.from_orm(user))

    @route("post", "/signup")
    async def signup(self, data: UserCreate, db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        try:
            user = await service.signup(data.dict())
            from app.models.user_schemas import UserResponse
            return self.payload_response(data=UserResponse.model_validate(user), message="Account created! Please check your email to verify your account.")
        except ValueError as e:
            return self.error_response(str(e), status_code=400)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Signup unexpected error: {str(e)}")
            return self.error_response(f"Backend error during signup: {str(e)}", status_code=500)

    @route("post", "/login")
    async def login(self, data: UserLogin, db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        try:
            res = await service.authenticate(data.email, data.password)
            if not res:
                return self.error_response("Invalid email or password", status_code=401)
            
            # Sanitization: Ensure the returned user object is stripped of sensitive fields
            from app.models.user_schemas import UserResponse
            if res.get("user"):
                res["user"] = UserResponse.model_validate(res["user"])
                
            return self.payload_response(data=res)
        except ValueError as e:
            # 403 for unverified, check if message contains "not verified"
            sc = 403 if "not verified" in str(e).lower() else 401
            return self.error_response(str(e), status_code=sc)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Login unexpected error: {str(e)}")
            return self.error_response(f"Backend error during login: {str(e)}", status_code=500)

    @route("post", "/refresh")
    async def refresh_token(self, data: dict, db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        try:
            res = await service.refresh_session(data.get("refresh_token"))
            return self.payload_response(data=res)
        except ValueError as e:
            return self.error_response(str(e), status_code=401)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Refresh error: {str(e)}")
            return self.error_response(f"Backend refresh error: {str(e)}", status_code=500)

    @route("post", "/resend-mfa")
    async def resend_mfa(self, data: dict, db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        try:
            res = await service.resend_mfa(data.get("email"))
            return self.payload_response(data=res)
        except ValueError as e:
            return self.error_response(str(e), status_code=400)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Resend MFA error: {str(e)}")
            return self.error_response(f"Backend error: {str(e)}", status_code=500)

    @route("post", "/verify-account")
    async def verify_account(self, data: UserVerify, db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        res = await service.verify_account(data.token)
        if res == "invalid":
            return self.error_response("Invalid or expired verification token", status_code=400)
        
        # Both "success" and "already_verified" are treated as successful for the UI
        msg = "Account verified successfully! You can now log in."
        if res == "already_verified":
            msg = "Account is already verified. Please sign in."
            
        return self.payload_response(data={}, message=msg)

    @route("post", "/logout")
    async def logout(self, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        await service.logout(current_user.id)
        return self.payload_response(data={}, message="Logged out successfully.")

    @route("post", "/forgot-password")
    async def forgot_password(self, data: dict, db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        await service.forgot_password(data.get("email"))
        return self.payload_response(data={}, message="If your email is registered, a reset link will be sent.")

    @route("post", "/reset-password")
    async def reset_password(self, data: dict, db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        try:
            await service.reset_password(data.get("token"), data.get("password"))
            return self.payload_response(data={}, message="Password updated successfully. Please login with your new password.")
        except ValueError as e:
            return self.error_response(str(e), status_code=400)

    @route("post", "/verify-mfa")
    async def verify_mfa(self, data: dict, db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        res = await service.verify_mfa_login(data.get("email"), data.get("code"))
        if not res:
            return self.error_response("Invalid or expired verification code", status_code=401)
            
        from app.models.user_schemas import UserResponse
        if res.get("user"):
            res["user"] = UserResponse.model_validate(res["user"])
            
        return self.payload_response(data=res, message="MFA Verified. Welcome!")

    @route("post", "/toggle-mfa")
    async def toggle_mfa(self, data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = UserService(db)
        user = await service.toggle_mfa(current_user.id, data.get("enabled", False))
        if not user:
            return self.error_response("Failed to toggle MFA", status_code=400)
            
        from app.models.user_schemas import UserResponse
        status_msg = "enabled" if user.mfa_enabled else "disabled"
        return self.payload_response(data=UserResponse.from_orm(user), message=f"Multi-factor authentication {status_msg}.")

    @route("get", "/me/eslips")
    async def get_eslips(self, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        from app.models.eslip_models import ESlip
        stmt = select(ESlip).where(ESlip.user_id == current_user.id).order_by(ESlip.generated_at.desc())
        result = await db.execute(stmt)
        items = result.scalars().all()
        return self.payload_response(data=items, one_record=False)

class TransactionController(BaseController):
    module = "transactions"
    tags = ["Transactions"]

    @route("post", "/upload")
    async def upload(self, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        if not (file.filename.endswith('.csv') or file.filename.endswith('.pdf')):
            return self.error_response("Only CSV and PDF files are supported", status_code=400)
            
        # Clean Architecture: Stream large files to disk instead of RAM
        os.makedirs("storage/statements", exist_ok=True)
        safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = f"storage/statements/{safe_filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        service = TransactionService(db)
        res = await service.process_upload(user_id=current_user.id, file_path=file_path, original_filename=file.filename)
        return self.payload_response(
            data=res, 
            message=f"Successfully processed {res['count']} transactions from {file.filename}"
        )


    @route("get", "/")
    async def list_transactions(self, page: int = 1, per_page: int = 10, 
                               document_id: Optional[int] = None, transaction_type: Optional[str] = None,
                               etims_validated: Optional[bool] = None, is_excluded: Optional[bool] = None,
                               current_user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
        service = TransactionService(db)
        filters = {"user_id": current_user.id}
        if document_id:
            filters["document_id"] = document_id
        if transaction_type:
            filters["transaction_type"] = transaction_type
        if etims_validated is not None:
            filters["etims_validated"] = etims_validated
        if is_excluded is not None:
            filters["is_excluded_from_etims"] = is_excluded
            
        items, total = await service.repository.list_paginated(filters=filters, page=page, per_page=per_page)
        
        pagination = {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "path": "/v1/transactions/"
        }
        return self.payload_response(data=items, one_record=False, pagination=pagination)

    @route("get", "/dashboard-summary")
    async def dashboard_summary(self, month: int, year: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = TransactionService(db)
        summary = await service.get_dashboard_summary(user_id=current_user.id, month=month, year=year)
        return self.payload_response(data=summary)

    @route("get", "/category-summary")
    async def category_summary(self, month: int, year: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        """
        Returns categorized Income/Expense breakdown for a given period.
        Used by the Tax Returns page to show the KRA-ready financial summary.
        """
        service = TransactionService(db)
        summary = await service.get_category_summary(user_id=current_user.id, month=month, year=year)
        return self.payload_response(data=summary)

    @route("get", "/export-itax")
    async def export_itax(self, type: str = "purchases", month: Optional[int] = None, year: Optional[int] = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        """Downloads a CSV ready for iTax Portal upload for a specific period"""
        service = TransactionService(db)
        if month and year:
            transactions = await service.repository.get_by_period(user_id=current_user.id, month=month, year=year)
        else:
            transactions = await service.get_by_user(user_id=current_user.id)
            
        csv_file = ExporterService.generate_itax_vat_csv(transactions, export_type=type)
        headers = {'Content-Disposition': f'attachment; filename="itax_{type}_export_{month}_{year}.csv"'}
        return StreamingResponse(csv_file, media_type='text/csv', headers=headers)

    @route("post", "/re-categorize")
    async def re_categorize(self, document_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = TransactionService(db)
        count = await service.re_categorize_all(user_id=current_user.id, document_id=document_id)
        return self.payload_response(data={"count": count}, message=f"Re-categorized {count} transactions.")

    @route("post", "/scan-etims")
    async def scan_etims(self, invoice_number: str, invoice_date: Optional[str] = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = TransactionService(db)
        result = await service.scan_and_save_etims(user_id=current_user.id, invoice_number=invoice_number, invoice_date=invoice_date)
        return self.payload_response(data=result, message="eTIMS invoice scanned and verified.")

class RuleController(BaseController):
    module = "rules"
    tags = ["Categorization Rules"]

    @route("get", "/")
    async def list_rules(self, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        service = RuleService(db)
        rules = await service.get_by_user(user_id=current_user.id)
        return self.payload_response(data=rules, one_record=False)

    @route("post", "/")
    async def create_rule(self, rule_data: dict, db: AsyncSession = Depends(get_db)):
        service = RuleService(db)
        rule = await service.create(rule_data)
        return self.payload_response(data=rule, message="Rule created successfully")

class TaxPeriodController(BaseController):
    module = "tax-periods"
    tags = ["Tax Periods & KRA APIs"]

    @route("post", "/file-nil")
    async def file_nil(self, data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        """
        File a NIL VAT/Income Tax return for a given period.
        Body: { "month": 12, "year": 2016, "obligation_code": "1" }
        """
        service = TaxPeriodService(db)
        month = data.get("month", 3)
        year = data.get("year", 2026)
        obligation_code = str(data.get("obligation_code", "5"))
        
        result = await service.reconcile_and_file_nil(
            user_id=current_user.id, month=month, year=year, obligation_code=obligation_code
        )
        
        if isinstance(result, dict) and result.get("Status") == "OK":
            return self.payload_response(
                data=result, 
                message=result.get("Message", "NIL return filed successfully.")
            )
        return self.error_response(
            result.get("Message", str(result)) if isinstance(result, dict) else str(result), 
            status_code=400
        )

    @route("get", "/obligations")
    async def get_obligations(self, pin: str):
        """
        Fetch all tax obligations for a KRA PIN.
        Sandbox test PINs: A744610021G, A948312567Q, A521040203F, P318295670X
        """
        from app.services.gava_service import GavaConnectService
        async with GavaConnectService() as gava:
            result = await gava.fetch_obligations(pin)
            if result.get("Status") == "OK":
                return self.payload_response(
                    data={"pin": pin, "obligations": result.get("ObligationsList", [])},
                    message=result.get("ResponseMsg", "Obligations retrieved.")
                )
            return self.error_response(result.get("ResponseMsg", "Failed to fetch obligations"), status_code=400)

    @route("post", "/validate-pin")
    async def validate_pin(self, data: dict):
        """
        Validate a KRA PIN and retrieve taxpayer details.
        Body: { "pin": "P318295670X" }
        Sandbox test PINs: A744610021G, A521040203F, P318295670X
        """
        pin = data.get("pin", "").strip().upper()
        if not pin:
            return self.error_response("PIN is required", status_code=400)
        
        from app.services.gava_service import GavaConnectService
        async with GavaConnectService() as gava:
            result = await gava.validate_pin(pin)
            if result.get("Status") == "OK":
                return self.payload_response(
                    data=result.get("PINDATA", result),
                    message=result.get("Message", "Valid PIN")
                )
            return self.error_response(
                result.get("Message", "Invalid or unknown PIN"), status_code=400
            )

    @route("post", "/validate-pin-by-id")
    async def validate_pin_by_id(self, data: dict):
        """
        Retrieve a taxpayer's KRA PIN using their National ID or Passport Number.
        Body: { "id_number": "12345678" }
        """
        id_number = data.get("id_number", "").strip()
        if not id_number:
            return self.error_response("id_number is required", status_code=400)
        
        from app.services.gava_service import GavaConnectService
        async with GavaConnectService() as gava:
            result = await gava.validate_pin_by_id(id_number)
            if result.get("Status") == "OK":
                return self.payload_response(
                    data=result.get("PINDATA", result),
                    message=result.get("Message", "PIN found for ID")
                )
            return self.error_response(
                result.get("Message", "ID Number not found in KRA system"), status_code=400
            )

    @route("post", "/check-invoice")
    async def check_invoice(self, data: dict):
        """
        Verify an eTIMS invoice number against the KRA registry.
        Body: { "invoice_number": "KRACU0100058659/5134", "invoice_date": "2024-08-18" }
        Sandbox test invoices:
          KRACU0100058659/5134  date: 2024-08-18
          KRACU0300001191/90697 date: 2020-06-13
        """
        invoice_number = data.get("invoice_number", "").strip()
        invoice_date = data.get("invoice_date")
        
        if not invoice_number:
            return self.error_response("invoice_number is required", status_code=400)
        
        from app.services.gava_service import GavaConnectService
        async with GavaConnectService() as gava:
            result = await gava.check_etims_invoice(invoice_number, invoice_date)
            # Success: KRA returns lowercase 'status' and 'responseCode' (int 40000)
            if result.get("status") == "OK" or result.get("responseCode") == 40000:
                return self.payload_response(
                    data=result.get("invoiceDetails", result),
                    message=result.get("responseDesc", "Invoice verified successfully.")
                )
            # Surface proper error: could be timeout, not found, or other KRA error
            err_msg = (
                result.get("Message")           # Our gava_service timeout/error message
                or result.get("responseDesc")   # KRA's own error description
                or f"Invoice check failed (code: {result.get('responseCode', 'unknown')})"
            )
            return self.error_response(err_msg, status_code=400)
