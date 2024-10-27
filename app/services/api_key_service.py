import hashlib
import secrets
import string
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from ..db.mongodb import MongoDB
from ..api.models.schemas import ApiKeyStatus, ApiKey, ApiKeyCreate

class ApiKeyService:
    def __init__(self):
        self.db = MongoDB()
        self.collection = self.db.client.memegen.api_keys

    def _generate_key(self, length: int = 32) -> str:
        """Generate a secure random API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _hash_key(self, key: str) -> str:
        """Hash the API key using SHA-256"""
        return hashlib.sha256(key.encode()).hexdigest()

    def create_api_key(self, key_data: ApiKeyCreate, created_by: Optional[str] = None) -> tuple[str, ApiKey]:
        """Create a new API key"""
        raw_key = self._generate_key()
        hashed_key = self._hash_key(raw_key)
        
        key_doc = {
            "key_id": str(ObjectId()),
            "name": key_data.name,
            "hashed_key": hashed_key,
            "status": ApiKeyStatus.ACTIVE,
            "created_at": datetime.now(),
            "permissions": key_data.permissions,
            "created_by": created_by,
            "last_used": None
        }
        
        self.collection.insert_one(key_doc)
        return f"{key_doc['key_id']}.{raw_key}", ApiKey(**key_doc)


    def validate_api_key(self, api_key: str) -> Optional[ApiKey]:
        """Validate an API key and update last used timestamp"""
        try:
            key_id, raw_key = api_key.split(".", 1)
            hashed_key = self._hash_key(raw_key)
            
            # Add expiration check
            current_time = datetime.now()
            
            key_doc = self.collection.find_one_and_update(
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

    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        result = self.collection.update_one(
            {
                "key_id": key_id,
                "status": ApiKeyStatus.ACTIVE  # Only revoke active keys
            },
            {"$set": {"status": ApiKeyStatus.REVOKED}}
        )
        return result.modified_count > 0


    def delete_api_key(self, key_id: str) -> bool:
            """Delete an API key"""
            result = self.collection.delete_one({"key_id": key_id})
            return result.deleted_count > 0

    def list_api_keys(self) -> List[ApiKey]:
            """List all API keys"""
            keys = self.collection.find({"status": ApiKeyStatus.ACTIVE})
            return [ApiKey(**key) for key in keys]

    ## other methods e.g. list_api_keys_by_status