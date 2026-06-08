from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base

# Import all models so Alembic/SQLAlchemy can see them
from app.models import models  # noqa

# Import routers
from app.api import auth, sales, inventory, stores, ai, reports, invoices

# ── Create tables (dev mode — use Alembic in production) ───────────────────
Base.metadata.create_all(bind=engine)

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="BizPulse API",
    description="Backend API for the BizPulse business management platform",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/v1")
app.include_router(sales.router,     prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(stores.router,    prefix="/api/v1")
app.include_router(ai.router,        prefix="/api/v1")
app.include_router(reports.router,   prefix="/api/v1")
app.include_router(invoices.router,  prefix="/api/v1")

# ── Health check ───────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "db": "connected"}
