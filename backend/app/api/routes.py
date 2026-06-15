from fastapi import APIRouter
from app.api import auth, drawings

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(drawings.router, prefix="/drawings", tags=["drawings"])
