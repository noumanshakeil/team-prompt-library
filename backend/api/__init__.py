from fastapi import APIRouter
from backend.api import health, library, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(library.router, prefix="/api", tags=["library"])
api_router.include_router(ui.router, tags=["ui"])
