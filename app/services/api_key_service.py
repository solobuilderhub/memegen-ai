import hashlib
import secrets
import string
from datetime import datetime
from typing import Optional, List, Tuple
from bson import ObjectId
from ..db.mongodb import MongoDB
from ..api.models.schemas import ApiKeyStatus, ApiKey, ApiKeyCreate

class ApiKeyService:
    def __init__(self, db: MongoDB):
        self.db = db
    
    def _generate_key(self, length: int = 32) -> str:
        """Generate a secure random API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _hash_key(self, key: str) -> str:
        """Hash the API key using SHA-256"""
        return hashlib.sha256(key.encode()).hexdigest()

    async def create_api_key(self, key_data: ApiKeyCreate, created_by: Optional[str] = None) -> Tuple[str, ApiKey]:
        """Create a new API key"""
        raw_key = self._generate_key()
        hashed_key = self._hash_key(raw_key)
        
        key_doc = {
            "key_id": str(ObjectId()),
            "name": key_data.name,
            "hashed_key": hashed_key,
            "status": ApiKeyStatus.ACTIVE,
            "created_at": datetime.utcnow(),
            "permissions": key_data.permissions,
            "created_by": created_by,
            "last_used": None
        }
        
        await self.db.api_keys.insert_one(key_doc)
        return f"{key_doc['key_id']}.{raw_key}", ApiKey(**key_doc)

    async def validate_api_key(self, api_key: str) -> Optional[ApiKey]:
        """Validate an API key and update last used timestamp"""
        try:
            key_id, raw_key = api_key.split(".", 1)
            hashed_key = self._hash_key(raw_key)
            
            current_time = datetime.utcnow()
            
            key_doc = await self.db.api_keys.find_one_and_update(
                {
                    "key_id": key_id,
                    "hashed_key": hashed_key,
                    "status": ApiKeyStatus.ACTIVE,
                },
                {
                    "$set": {"last_used": current_time}
                },
                return_document=True
            )
            
            if not key_doc:
                return None
                
            return ApiKey(**key_doc)
                
        except Exception:
            return None

    async def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        result = await self.db.api_keys.update_one(
            {
                "key_id": key_id,
                "status": ApiKeyStatus.ACTIVE
            },
            {"$set": {"status": ApiKeyStatus.REVOKED}}
        )
        return result.modified_count > 0

    async def delete_api_key(self, key_id: str) -> bool:
        """Delete an API key"""
        result = await self.db.api_keys.delete_one({"key_id": key_id})
        return result.deleted_count > 0

    async def list_api_keys(self, skip: int = 0, limit: int = 100) -> List[ApiKey]:
        """List all API keys with pagination"""
        cursor = self.db.api_keys.find({"status": ApiKeyStatus.ACTIVE}) \
                               .skip(skip) \
                               .limit(limit)
        return [ApiKey(**key) async for key in cursor]

    async def get_api_key(self, key_id: str) -> Optional[ApiKey]:
        """Get a specific API key by ID"""
        key_doc = await self.db.api_keys.find_one({"key_id": key_id})
        return ApiKey(**key_doc) if key_doc else None

    async def list_api_keys_by_status(self, status: ApiKeyStatus, skip: int = 0, limit: int = 100) -> List[ApiKey]:
        """List API keys by status with pagination"""
        cursor = self.db.api_keys.find({"status": status}) \
                               .skip(skip) \
                               .limit(limit)
        return [ApiKey(**key) async for key in cursor]

    async def count_api_keys(self, status: Optional[ApiKeyStatus] = None) -> int:
        """Count total API keys, optionally filtered by status"""
        filter_query = {"status": status} if status else {}
        return await self.db.api_keys.count_documents(filter_query)