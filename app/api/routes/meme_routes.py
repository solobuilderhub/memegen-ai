import os
from fastapi import APIRouter, HTTPException, Depends
from ..models.schemas import MemeRequest, MemeResponse, ApiKey
from ...services import MemeService, OpenAIService, S3Service
from ...utils import ImageProcessor, TextOverlay
from ...utils.prompts import get_meme_system_prompt
from ...core.security import get_api_key, require_permissions
from typing import Annotated
from ...dependencies import get_meme_service

router = APIRouter(prefix="", tags=["meme"])

@router.post("/generate-meme", response_model=MemeResponse)
async def generate_meme(
    request: MemeRequest,
    api_key: ApiKey = Depends(require_permissions(["generate_meme"])),
    meme_service: MemeService = Depends(get_meme_service),
): 
    
    text_overlay = TextOverlay()

    try: 
        # Get random meme template
        meme_template = await meme_service.get_random_meme()

        image_bytes = ImageProcessor.download_image(meme_template['src']['url'])

        user_prompt = f"""
<Meme Template>
{meme_template['src']['name']}:
box_count:{meme_template['src']['box_count']} 
Annotations Guide for box:
{meme_template['annotations']}
</Meme Template>

Base on the template above give meme data in json for the following context:
{request.query}
        """
        system_prompt = get_meme_system_prompt()
        print("Calling ai")
        # analysis = {'annotations': [{'x': 616, 'y': 19, 'width': 559, 'height': 538, 'text': 'When you see your crush...', 'font_size': 80, 'font_name': 'Impact.ttf', 'stroke_width': 2, 'text_color': [255, 255, 255], 'outline_color': [0, 0, 0], 'padding': 10}, {'x': 616, 'y': 609, 'width': 546, 'height': 574, 'text': "...but you remember you're awkward.", 'font_size': 80, 'font_name': 'Impact.ttf', 'stroke_width': 2, 'text_color': [255, 255, 255], 'outline_color': [0, 0, 0], 'padding': 10}]}
        analysis = OpenAIService.analyze_image(system_prompt, user_prompt, image_bytes)
    
        # print(type(analysis))
        # print(analysis)
        # Add text to image
        meme = text_overlay.add_multiple_texts(image_bytes, analysis['annotations'])
        # print("Meme generated", meme)
     
        
        # ================Test the image================
        # test the image .. comment out later
        # Ensure the /images directory exists
        # os.makedirs("images", exist_ok=True)

        # Save the generated meme to the /images directory
        # with open("images/generated_meme.jpg", "wb") as f:
        #     f.write(meme.getbuffer())
        # ================End test================

        meme_data = S3Service.upload_image(meme)

        # res = ({"url": "https://via.placeholder.com/512x512.png", "expiry_date": system_prompt, "presigned_url": "https://via.placeholder.com/512x512.png"})
        return MemeResponse(**meme_data)
    except Exception as e:
        print(f"Error generating meme: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/image-to-meme", response_model=MemeResponse)
# async def image_to_meme(
#     request: MemeRequest,
#     api_key: ApiKey = Depends(require_permissions(["generate_meme"])),
#     meme_service: MemeService = Depends(get_meme_service),
#     openai_service: OpenAIService = Depends(get_openai_service),
#     s3_service: S3Service = Depends(get_s3_service),
#     img_processor: ImageProcessor = Depends(get_image_processor),
# ):
#     try:
#         # Get random meme template
#         meme_template = meme_service.get_random_meme()
        
#         # Download the template
#         image_bytes = img_processor.download_image(meme_template['url'])
        
#         # Add image dimension, name and box count to the context
#         context = (
#             f'Image dimensions: 512x512 (reference size), '
#             f'Original dimensions: {meme_template["width"]}x{meme_template["height"]}, '
#             f'Name: {meme_template["name"]}, '
#             f'Box count: {meme_template["box_count"]}. '
#             f'Please position text within 512x512 coordinates, '
#             f'the system will automatically scale to original dimensions.'
#         )
#         # print('Context:', context)
        
#         # Analyze with GPT-4 and get text positions
#         analysis = openai_service.analyze_image(image_bytes, request.query, context)
#         # print('AI Analysis:', analysis)

#         # Generate new meme
#         new_meme = img_processor.generate_meme_from_text_boxes(image_bytes, analysis['text_boxes'])
#         # ================Test the image================
#         # test the image .. comment out later
#         # Ensure the /images directory exists
#         # os.makedirs("images", exist_ok=True)

#         # Save the generated meme to the /images directory
#         # with open("images/generated_meme.jpg", "wb") as f:
#         #     f.write(new_meme.getbuffer())
#         # ================End test================
        
#         # Upload to S3
#         meme_data = s3_service.upload_image(new_meme)
        
#         return MemeResponse(**meme_data)
    
#     except Exception as e:
#         print(f"Error generating meme: {str(e)}")  # Add logging
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(api_key: Annotated[str, Depends(get_api_key)]):
    return {"status": "healthy"}