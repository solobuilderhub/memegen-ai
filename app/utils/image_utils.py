import base64
from PIL import Image, ImageDraw
from typing import  Dict, List
import io
import requests
from .text_styler import TextStyler

class ImageProcessor:
    def __init__(self):
        self.styler = TextStyler()

    def encode_image(self, image_bytes):
        return base64.b64encode(image_bytes.getvalue()).decode('utf-8')


    def download_image(self, url: str) -> io.BytesIO:
        """
        Download image from the provided URL.
        """
        response = requests.get(url)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        raise Exception(f"Failed to download image from {url}")

    def generate_meme_from_text_boxes(self, image_bytes: io.BytesIO, text_boxes: List[Dict]) -> io.BytesIO:
        """
        Generate meme by placing text within specified bounding boxes.
        """
        # Open the original image
        img = Image.open(image_bytes).convert('RGBA')
        original_width, original_height = img.size

        # Create a transparent overlay for text
        text_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_overlay)

        for box in text_boxes:
            # Adjust bounding box coordinates based on original image size
            scale_x = original_width / 512
            scale_y = original_height / 512
            adjusted_box = {
                "x": int(box['x'] * scale_x),
                "y": int(box['y'] * scale_y),
                "width": int(box['width'] * scale_x),
                "height": int(box['height'] * scale_y),
                "text": box['text'],
                "font_size": int(box['font_size'] * min(scale_x, scale_y)),
                "color": box['color'],
                "style": box['style']
            }

            # Create text layer for each box
            text_layer = self.styler.create_text_layer(
                image_size=img.size,
                text_box=adjusted_box
            )

            # Composite the text layer onto the overlay
            text_overlay = Image.alpha_composite(text_overlay, text_layer)

        # Composite the text overlay onto the original image
        final_img = Image.alpha_composite(img, text_overlay)

        # Convert to RGB for JPEG
        final_img = final_img.convert('RGB')

        # Save to buffer
        output = io.BytesIO()
        final_img.save(output, format='JPEG', quality=95)
        output.seek(0)
        return output

