from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from typing import Optional, List
from ..services.api_key_service import ApiKeyService
from ..api.models.schemas import ApiKey, ApiKeyStatus

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class ApiKeyAuth:
    def __init__(self, required_permissions: Optional[List[str]] = None):
        self.api_key_service = ApiKeyService()
        self.required_permissions = required_permissions

    async def __call__(
        self,
        api_key_header: str = Security(api_key_header)
    ) -> ApiKey:
        if not api_key_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key header is missing",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        api_key = self.api_key_service.validate_api_key(api_key_header)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        if api_key.status != ApiKeyStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key is not active",
            )

        if self.required_permissions:
            missing_permissions = [
                perm for perm in self.required_permissions 
                if perm not in api_key.permissions
            ]
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing_permissions)}",
                )

        return api_key
    

# Define a dependency that requires the API key
get_api_key = ApiKeyAuth()

def require_permissions(permissions: List[str]):
    return ApiKeyAuth(required_permissions=permissions)