from pymongo import MongoClient
from datetime import datetime, timedelta
from ..config.settings import get_settings

settings = get_settings()

class MongoDB:
    def __init__(self):
        self.client = MongoClient(settings.mongo_uri)
        self.db = self.client.memegen
        self.meme_templates = self.db.meme_templates

    def get_meme_templates(self):
        """Get meme templates from cache or update if expired"""
        cache = self.meme_templates.find_one({"type": "meme_cache"})
        
        if not cache or self._is_cache_expired(cache):
            return None
        
        return cache["templates"]

    def update_meme_templates(self, templates):
        """Update meme templates in cache"""
        self.meme_templates.update_one(
            {"type": "meme_cache"},
            {
                "$set": {
                    "templates": templates,
                    "last_updated": datetime.utcnow(),
                    "type": "meme_cache"
                }
            },
            upsert=True
        )

    def _is_cache_expired(self, cache):
        """Check if cache is older than 7 days"""
        last_updated = cache.get("last_updated")
        if not last_updated:
            return True
        return (datetime.utcnow() - last_updated) > timedelta(days=7)

    def save_generated_meme(self, meme_data):
        """Save generated meme details"""
        return self.db.generated_memes.insert_one({
            **meme_data,
            "created_at": datetime.utcnow()
        })