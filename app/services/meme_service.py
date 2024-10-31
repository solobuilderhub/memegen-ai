from fastapi import HTTPException
from bson import ObjectId
from ..api.models.schemas import MemeTemplate, MemeTemplateUpdate
from typing import List

class MemeService:
    def __init__(self, db):
        self.db = db

    async def create_template(self, template: MemeTemplate) -> dict:
        result = await self.db.meme_templates.insert_one(template.model_dump())
        return {"id": str(result.inserted_id), **template.model_dump()}

    async def get_template(self, template_id: str) -> dict:
        try:
            template = await self.db.meme_templates.find_one({"_id": ObjectId(template_id)})
            if template:
                return {"id": str(template["_id"]), **{k: v for k, v in template.items() if k != "_id"}}
            raise HTTPException(status_code=404, detail="Template not found")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_all_templates(self) -> List[dict]:
        templates = []
        async for template in self.db.meme_templates.find():
            templates.append(
                {"id": str(template["_id"]), **{k: v for k, v in template.items() if k != "_id"}}
            )
        return templates

    async def update_template(self, template_id: str, template_update: MemeTemplateUpdate) -> dict:
        try:
            update_data = {
                k: v for k, v in template_update.model_dump(exclude_unset=True).items() if v is not None
            }
            
            result = await self.db.meme_templates.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=404, detail="Template not found")
                
            return await self.get_template(template_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_template(self, template_id: str) -> dict:
        try:
            result = await self.db.meme_templates.delete_one({"_id": ObjectId(template_id)})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Template not found")
            return {"message": "Template deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_random_meme(self) -> dict:
        try:
            # Using MongoDB's aggregation pipeline to get a random document
            pipeline = [{"$sample": {"size": 1}}]
            async for template in self.db.meme_templates.aggregate(pipeline):
                return {k: v for k, v in template.items() if k != "_id"}
            raise HTTPException(status_code=404, detail="No templates found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))