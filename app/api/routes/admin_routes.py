from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.schemas import ApiKeyCreate, ApiKey
from ...services.api_key_service import ApiKeyService
from ...core.security import require_permissions

router = APIRouter()
api_key_service = ApiKeyService()

# app/routes/admin_routes.py

@router.post("/api-keys", response_model=dict)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_key: ApiKey = Depends(require_permissions(["admin"]))
):
    raw_key, key_info = api_key_service.create_api_key(
        key_data,
        created_by=current_key.key_id
    )
    return {
        "api_key": raw_key,
        "key_info": key_info
    }

@router.get("/api-keys", response_model=List[ApiKey])
async def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    current_key: ApiKey = Depends(require_permissions(["admin"]))
):
    return api_key_service.list_api_keys(skip, limit)

@router.post("/api-keys/{key_id}/revoke")
async def revoke_api_key(
    key_id: str,
    current_key: ApiKey = Depends(require_permissions(["admin"]))
):
    if current_key.key_id == key_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot revoke your own API key"
        )
    
    if api_key_service.revoke_api_key(key_id):
        return {"message": "API key revoked successfully"}
    raise HTTPException(status_code=404, detail="API key not found")