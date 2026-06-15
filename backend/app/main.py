from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.core.config import settings

app = FastAPI(
    title="AeroFAI AI",
    version="0.1.0",
    description="AS9102 First Article Inspection platform backend",
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
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    # TODO: initialize database connections, cache, and task queue
    pass


@app.on_event("shutdown")
def on_shutdown():
    # TODO: gracefully close external resources
    pass
