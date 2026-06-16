from fastapi import APIRouter
from . import auth, drawings, results, enhanced_drawings

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(drawings.router, prefix="/drawings", tags=["drawings"])
api_router.include_router(results.router, prefix="/drawings", tags=["results"])
api_router.include_router(enhanced_drawings.router, prefix="/drawings", tags=["enhanced_drawings"])
