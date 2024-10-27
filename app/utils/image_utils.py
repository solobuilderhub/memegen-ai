import base64
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from typing import List, Dict, Tuple

def encode_image(image_bytes):
    return base64.b64encode(image_bytes.getvalue()).decode('utf-8')

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    raise Exception("Failed to download image")

def scale_coordinates(
    point: Tuple[int, int], 
    original_dims: Tuple[int, int], 
    processed_dims: Tuple[int, int] = (512, 512)
) -> Tuple[int, int]:
    """Scale coordinates from processed dimensions back to original dimensions."""
    scale_x = original_dims[0] / processed_dims[0]
    scale_y = original_dims[1] / processed_dims[1]
    
    return (
        int(point[0] * scale_x),
        int(point[1] * scale_y)
    )

def scale_positions(
    positions: List[Dict], 
    original_dims: Tuple[int, int],
    processed_dims: Tuple[int, int] = (512, 512)
) -> List[Dict]:
    """Scale all text positions and font sizes to match original image dimensions."""
    scaled_positions = []
    scale_factor = min(
        original_dims[0] / processed_dims[0],
        original_dims[1] / processed_dims[1]
    )
    
    for pos in positions:
        scaled_x, scaled_y = scale_coordinates(
            (pos['x'], pos['y']),
            original_dims,
            processed_dims
        )
        
        scaled_font_size = int(pos['font_size'] * scale_factor)
        
        scaled_positions.append({
            'x': scaled_x,
            'y': scaled_y,
            'font_size': scaled_font_size,
            'text': pos['text']
        })
    
    return scaled_positions

def generate_meme_from_image(image_bytes, text_positions):
    print("Generating meme...")
    img = Image.open(image_bytes)
    original_dims = img.size
    
    # Scale positions to match original image dimensions
    scaled_positions = scale_positions(text_positions, original_dims)
    
    draw = ImageDraw.Draw(img)
    
    for position in scaled_positions:
        try:
            font = ImageFont.truetype("arial.ttf", position['font_size'])
        except OSError:
            # Fallback to default font if arial.ttf is not available
            font = ImageFont.load_default()
            
        # Get text size for centering
        text_bbox = draw.textbbox(
            (position['x'], position['y']),
            position['text'],
            font=font
        )
        text_width = text_bbox[2] - text_bbox[0]
        
        # Center text horizontally around the x coordinate
        x = position['x'] - (text_width // 2)
        
        draw.text(
            (x, position['y']),
            position['text'],
            font=font,
            fill='white',
            stroke_width=2,
            stroke_fill='black'
        )
    
    output = io.BytesIO()
    img.save(output, format='JPEG')
    output.seek(0)
    return output