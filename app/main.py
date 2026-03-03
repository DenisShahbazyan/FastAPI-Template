from fastapi import FastAPI

from app.api.routers import main_router
from app.core.middleware.cors import add_cors_middleware

app = FastAPI(
    redoc_url=None,
)

add_cors_middleware(app)
app.include_router(main_router)
