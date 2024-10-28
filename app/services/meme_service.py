import requests
import random
from fastapi import HTTPException
from ..config.settings import get_settings
from ..db.mongodb import MongoDB

settings = get_settings()

class MemeService:
    def __init__(self):
        self.db = MongoDB()

    def get_random_meme(self):

        try:
            # Try to get memes from cache
            memes = self.db.get_meme_templates()
            
            # If cache is empty or expired, fetch from API
            if not memes:
                memes = self._fetch_and_cache_memes()
            
            return random.choice(memes)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
    def _fetch_and_cache_memes(self):
        """Fetch memes from API and cache them"""
        response = requests.get("https://api.imgflip.com/get_memes")
        if response.status_code == 200:
            memes = response.json()['data']['memes']
            self.db.update_meme_templates(memes)
            return memes
        raise HTTPException(status_code=500, detail="Failed to fetch memes")

    def save_generated_meme(self, meme_url, text_positions, query, template_id):
        """Save generated meme details"""
        meme_data = {
            "meme_url": meme_url,
            "text_positions": text_positions,
            "query": query,
            "template_id": template_id
        }
        self.db.save_generated_meme(meme_data)
        return meme_data

        