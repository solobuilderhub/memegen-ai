from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from ..config.settings import get_settings

settings = get_settings()


class MongoDB:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
        self.meme_templates = None
        self.api_keys = None

    async def connect_to_database(self):
        try:
            self.client = AsyncIOMotorClient(
                settings.mongo_uri,
                maxPoolSize=10,
                minPoolSize=5,
                maxIdleTimeMs=50000
            )
            self.db = self.client.memegen
            self.meme_templates = self.db.meme_templates
            self.api_keys = self.db.api_keys
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise e

    async def close_database_connection(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.meme_templates = None
            self.api_keys = None