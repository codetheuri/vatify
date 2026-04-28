from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from app.core.db import init_db
from app.controllers.controllers import TransactionController, RuleController, TaxPeriodController, UserController, DocumentController
from app.common.exceptions.handler import validation_exception_handler

# Import models to ensure they are registered with SQLModel/SQLAlchemy
from app.models.user_models import User
from app.models.transaction_models import TaxTransaction, CategoryRule, TaxPeriod, TaxDocument

app = FastAPI(
    title="TaxAgent API",
    description="KRA iTax Return Preparation Assistant",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

# Register Controllers
transactions_ctrl = TransactionController()
app.include_router(transactions_ctrl.router)

rules_ctrl = RuleController()
app.include_router(rules_ctrl.router)

tax_period_ctrl = TaxPeriodController()
app.include_router(tax_period_ctrl.router)

user_ctrl = UserController()
app.include_router(user_ctrl.router)

doc_ctrl = DocumentController()
app.include_router(doc_ctrl.router)

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the TaxAgent API", "docs": "/docs"}

@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
