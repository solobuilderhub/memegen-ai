from openai import AzureOpenAI
import json
from functools import lru_cache
from ..config.settings import get_settings
from ..utils.image_utils import ImageProcessor

settings = get_settings()

# Cache the client creation
@lru_cache()
def get_openai_client():
    return AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_endpoint=settings.azure_openai_api_endpoint
    )

class OpenAIService:
    @staticmethod
    def analyze_image(system_prompt: str, user_prompt: str, image_bytes: bytes) -> dict:
        client = get_openai_client()
        img_processor = ImageProcessor()
        base64_image = img_processor.encode_image(image_bytes)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low"
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)