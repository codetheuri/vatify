import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import engine, AsyncSessionLocal
from app.models.user_models import User
from app.models.transaction_models import CategoryRule
from sqlmodel import select

async def seed():
    async with AsyncSessionLocal() as session:
        # Check if user exists
        stmt = select(User).where(User.email == "joseph@taxagent.ke")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print("Seeding user...")
            user = User(
                email="joseph@taxagent.ke",
                hashed_password="taxagent2026",
                full_name="Joseph Developer",
                phone_number="0706063617",
                id_number="41764982",
                kra_pin="A019914707A",
                business_name="TaxAgent Solutions",
                tax_obligation="VAT"
            )
            session.add(user)
            await session.flush()

            # Seed some basic rules
            rules = [
                CategoryRule(pattern="KPLC", category="Utilities", transaction_type="Expense", user_id=user.id),
                CategoryRule(pattern="Quickmart", category="Supplies", transaction_type="Expense", user_id=user.id),
                CategoryRule(pattern="Safaricom", category="Communication", transaction_type="Expense", user_id=user.id),
            ]
            for r in rules: session.add(r)
            
            await session.commit()
            print("Seeding completed.")
        else:
            print("User already exists.")

if __name__ == "__main__":
    asyncio.run(seed())
