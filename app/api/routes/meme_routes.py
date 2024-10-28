from fastapi import APIRouter, HTTPException, Depends
from ..models.schemas import MemeRequest, MemeResponse, ApiKey
from ...services.meme_service import MemeService
from ...services.openai_service import OpenAIService
from ...services.s3_service import S3Service
from ...utils.image_utils import ImageProcessor
from ...core.security import get_api_key, require_permissions
import os
from typing import Annotated

router = APIRouter()

@router.post("/generate-meme", response_model=MemeResponse)
async def generate_meme(
    request: MemeRequest,
    api_key: ApiKey = Depends(require_permissions(["generate_meme"]))
):
    try:
        # Initialize services
        meme_service = MemeService()
        openai_service = OpenAIService()
        s3_service = S3Service()
        img_processor = ImageProcessor()

        # Get random meme template
        meme_template = meme_service.get_random_meme()
        
        # Download the template
        image_bytes = img_processor.download_image(meme_template['url'])
        
        # Add image dimension, name and box count to the context
        context = (
            f'Image dimensions: 512x512 (reference size), '
            f'Original dimensions: {meme_template["width"]}x{meme_template["height"]}, '
            f'Name: {meme_template["name"]}, '
            f'Box count: {meme_template["box_count"]}. '
            f'Please position text within 512x512 coordinates, '
            f'the system will automatically scale to original dimensions.'
        )
        # print('Context:', context)
        
        # Analyze with GPT-4 and get text positions
        analysis = openai_service.analyze_image(image_bytes, request.query, context)
        # print('AI Analysis:', analysis)

        # Generate new meme
        new_meme = img_processor.generate_meme_from_text_boxes(image_bytes, analysis['text_boxes'])
        # ================Test the image================
        # test the image .. comment out later
        # Ensure the /images directory exists
        # os.makedirs("images", exist_ok=True)

        # Save the generated meme to the /images directory
        # with open("images/generated_meme.jpg", "wb") as f:
        #     f.write(new_meme.getbuffer())
        # ================End test================
        
        # Upload to S3
        meme_data = s3_service.upload_image(new_meme)
        
        return MemeResponse(**meme_data)
    
    except Exception as e:
        print(f"Error generating meme: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(api_key: Annotated[str, Depends(get_api_key)]):
    return {"status": "healthy"}