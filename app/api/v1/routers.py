from fastapi import APIRouter

from app.api.v1.endpoints import user_router

v1_router = APIRouter()

v1_router.include_router(user_router)
