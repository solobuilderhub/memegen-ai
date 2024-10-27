from openai import AzureOpenAI
import json
from ..config.settings import get_settings
from ..utils.image_utils import encode_image
from ..utils.prompts import SYSTEM_PROMPT, generate_user_prompt  # Adjust the import path as needed

settings = get_settings()

class OpenAIService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_api_endpoint
        )

    def analyze_image(self, image_bytes, query, context):
        # Uncomment the test response if needed for debugging
        # test_res = '''{
        # "text_positions": [
        #     {
        #         "x": 100,
        #         "y": 100,
        #         "font_size": 24,
        #         "text": "When you finally understand"
        #     },
        #     {
        #         "x": 100,
        #         "y": 200,
        #         "font_size": 24,
        #         "text": "the plot twist in your favorite show"
        #     }
        # ]
        # }'''
        # parsed_res = json.loads(test_res)
        # return parsed_res

        base64_image = encode_image(image_bytes)
        
        user_prompt = generate_user_prompt(context, query)
        
        # print('User Prompt', user_prompt)

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt,
                        },
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
