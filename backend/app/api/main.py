from fastapi import APIRouter

from app.api.routers import auth, materials,session
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(materials.router)
api_router.include_router(session.router)
