from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.schemas import MemeTemplate, MemeTemplateResponse, MemeTemplateUpdate
from ...services.meme_service import MemeService
from ...core.security import require_permissions
from ...dependencies import get_meme_service

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("", response_model=MemeTemplateResponse)
async def create_template(
    template: MemeTemplate,
    meme_service: MemeService = Depends(get_meme_service),
    _=Depends(require_permissions(["manage_templates"]))
):
    return await meme_service.create_template(template)

@router.get("/{template_id}", response_model=MemeTemplateResponse)
async def get_template(
    template_id: str,
    meme_service: MemeService = Depends(get_meme_service),
    _=Depends(require_permissions(["read_templates"]))
):
    return await meme_service.get_template(template_id)

@router.get("", response_model=List[MemeTemplateResponse])
async def get_all_templates(
    meme_service: MemeService = Depends(get_meme_service),
    _=Depends(require_permissions(["read_templates"]))
):
    return await meme_service.get_all_templates()

@router.put("/{template_id}", response_model=MemeTemplateResponse)
async def update_template(
    template_id: str,
    template_update: MemeTemplateUpdate,
    meme_service: MemeService = Depends(get_meme_service),
    _=Depends(require_permissions(["manage_templates"]))
):
    return await meme_service.update_template(template_id, template_update)

@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    meme_service: MemeService = Depends(get_meme_service),
    _=Depends(require_permissions(["manage_templates"]))
):
    return await meme_service.delete_template(template_id)

@router.get("/random/meme", response_model=MemeTemplateResponse)
async def get_random_template(
    meme_service: MemeService = Depends(get_meme_service),
    _=Depends(require_permissions(["read_templates"]))
):
    return await meme_service.get_random_meme()