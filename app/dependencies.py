from typing import AsyncGenerator
from fastapi import Depends
from .config.settings import get_settings
from .db.mongodb import MongoDB
from .services import  ApiKeyService, MemeService

## About dependencies injection in fastapi
"""
FastAPI uses dependency injection to manage the dependencies of your route functions.
"""

settings = get_settings()

db = MongoDB()

async def get_database() -> AsyncGenerator[MongoDB, None]:
    if db.client is None:
        await db.connect_to_database()
    try:
        yield db
    finally:
        pass


async def get_api_key_service(db: MongoDB = Depends(get_database)) -> ApiKeyService:
    return ApiKeyService(db)

async def get_meme_service(db=Depends(get_database)):
    return MemeService(db)