from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .api.routes import api_router
from .core.config import settings
from .core.database import init_db, close_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for app startup and shutdown."""
    # Startup
    logger.info("Starting up AeroFAI backend...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AeroFAI backend...")
    await close_db()
    logger.info("Database connection closed")


app = FastAPI(
    title="AeroFAI AI",
    version="0.1.0",
    description="AS9102 First Article Inspection platform backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}
