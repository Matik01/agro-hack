from fastapi import FastAPI
from app.api.v1.routes import router
from app.config.config import get_settings
import uvicorn

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

app.include_router(router, prefix=settings.API_V1_PREFIX)
