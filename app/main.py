from fastapi import FastAPI

from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.invoices import router as invoices_router
from app.routers.batches import router as batches_router
from app.routers.line_items import router as line_items_router
from app.routers.qa_reviews import router as qa_reviews_router
from app.routers.admin import router as admin_router

# Create FastAPI application instance
app = FastAPI(title="Pharma Invoice Verification API")

# Register routers
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(invoices_router)
app.include_router(batches_router)
app.include_router(line_items_router)
app.include_router(qa_reviews_router)
app.include_router(admin_router)
