from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine

# Import models so SQLAlchemy registers them against Base before create_all runs.
from app.models import user, run, transaction, flag, audit_log  # noqa: F401

from app.auth.routes import router as auth_router
from app.ingestion.routes import router as ingestion_router
from app.review.routes import router as review_router
from app.audit.routes import router as audit_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ledger API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(review_router)
app.include_router(audit_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
