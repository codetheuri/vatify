from sqlalchemy import select, func, and_
from typing import List, Optional
from app.common.base.base_repository import BaseRepository
from app.models.transaction_models import TaxTransaction, CategoryRule, TaxPeriod, TaxDocument
from app.models.user_models import User

class TransactionRepository(BaseRepository[TaxTransaction]):
    model = TaxTransaction

    async def get_by_user(self, user_id: int) -> List[TaxTransaction]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_unvalidated_etims(self, user_id: int) -> List[TaxTransaction]:
        """
        Find expenses that require eTIMS but haven't been validated.
        """
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.transaction_type == "Expense",
                self.model.etims_validated == False,
                self.model.is_excluded_from_etims == False
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_period(self, user_id: int, month: int, year: int) -> List[TaxTransaction]:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                func.strftime('%m', self.model.date) == f"{month:02}",
                func.strftime('%Y', self.model.date) == str(year)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_totals_for_period(self, user_id: int, month: int, year: int) -> dict:
        """
        Calculate total income, expense, and tax component for a period.
        """
        stmt = select(
            self.model.transaction_type,
            func.sum(self.model.amount).label("total_amount"),
            func.sum(self.model.tax_amount).label("total_tax")
        ).where(
            and_(
                self.model.user_id == user_id,
                func.strftime('%m', self.model.date) == f"{month:02}",
                func.strftime('%Y', self.model.date) == str(year)
            )
        ).group_by(self.model.transaction_type)
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        totals = {"Income": {"amount": 0, "tax": 0}, "Expense": {"amount": 0, "tax": 0}}
        for row in rows:
            totals[row.transaction_type] = {"amount": row.total_amount, "tax": row.total_tax}
        return totals

    async def get_category_summary(self, user_id: int, month: int, year: int):
        """
        Returns per-category aggregates for a given month/year.
        Groups by transaction_type then category, summing amount and vat.
        Used for the KRA financial breakdown report.
        """
        stmt = select(
            self.model.transaction_type,
            self.model.category,
            func.count(self.model.id).label("tx_count"),
            func.sum(self.model.amount).label("total_amount"),
            func.sum(self.model.tax_amount).label("total_vat")
        ).where(
            and_(
                self.model.user_id == user_id,
                func.strftime('%m', self.model.date) == f"{month:02}",
                func.strftime('%Y', self.model.date) == str(year)
            )
        ).group_by(self.model.transaction_type, self.model.category)
        
        result = await self.session.execute(stmt)
        return result.all()  # List of Row objects

class RuleRepository(BaseRepository[CategoryRule]):
    model = CategoryRule

    async def get_by_user(self, user_id: int, active_only: bool = True) -> List[CategoryRule]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        if active_only:
            stmt = stmt.where(self.model.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

class TaxPeriodRepository(BaseRepository[TaxPeriod]):
    model = TaxPeriod

    async def get_period(self, user_id: int, month: int, year: int) -> Optional[TaxPeriod]:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.month == month,
                self.model.year == year
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

class DocumentRepository(BaseRepository[TaxDocument]):
    model = TaxDocument

    async def get_by_user(self, user_id: int) -> List[TaxDocument]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
