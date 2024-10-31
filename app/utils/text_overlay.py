from PIL import Image, ImageDraw, ImageFont
from .font_utils import get_font_path
import io
import logging

class TextOverlay:
    """
    A class to handle adding text overlays to images with wrapping and outline effects.
    """
    
    def __init__(self):
        """Initialize TextOverlay."""
        pass

    def _get_font(self, font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
        """
        Get font object for the specified font name and size.
        Falls back to PIL's default font if the requested font is not available.
        
        Args:
            font_name (str): Name of the font file
            font_size (int): Size of the font
            
        Returns:
            ImageFont: Font object
        """
        try:
            # First try to get the specified font
            font_path = get_font_path(font_name)
            return ImageFont.truetype(font_path, size=font_size)

        except Exception as e:
            logging.error(f"Failed to load the font. Error: {e}")
            return ImageFont.load_default()
            

    def _wrap_text(self, text: str, max_width: int, font: ImageFont.FreeTypeFont) -> list:
        """
        Internal method to wrap text for a given pixel width.

        Args:
            text (str): The text to wrap
            max_width (int): The maximum width in pixels
            font (ImageFont): The font object to use for text measurements

        Returns:
            list: A list of wrapped lines
        """
        lines = []
        words = text.split()
        if not words:
            return lines

        line = words[0]
        for word in words[1:]:
            test_line = f"{line} {word}"
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)
        return lines

    def add_text(self, image: Image.Image, annotation: dict) -> Image.Image:
        """
        Add wrapped text with outline to an image.

        Args:
            image_path (str | Image.Image| import io): Path to the input image or PIL Image object or io.BytesIO
            annotation (dict): Dictionary containing text parameters:
                {
                    "x": int,              # X coordinate
                    "y": int,              # Y coordinate
                    "width": int,          # Maximum width of text box
                    "height": int,         # Maximum height of text box
                    "text": str,           # Text to display
                    "font_size": int,      # Font size
                    "font_name": str,      # Font file name
                    "text_color": list,    # RGB color tuple for text
                    "outline_color": list, # RGB color tuple for outline
                    "stroke_width": int,   # Width of outline
                    "padding": int         # Padding around text
                }

        Returns:
            PIL.Image: Modified image with text overlay
        """
        try: 
            draw = ImageDraw.Draw(image)

            # Extract parameters from annotation
            text = annotation["text"]
            max_width = annotation["width"]
            max_height = annotation["height"]
            x, y = annotation["x"], annotation["y"]
            font_size = annotation.get("font_size", 40)
            font_name = annotation.get("font_name", "Arial.ttf")
            text_color = tuple(annotation.get("text_color", [255, 255, 255]))
            outline_color = tuple(annotation.get("outline_color", [0, 0, 0]))
            stroke_width = annotation.get("stroke_width", 2)
            padding = annotation.get("padding", 20)

            # Get font
            font = self._get_font(font_name, font_size)
        
            # Calculate effective dimensions
            effective_width = max_width - (2 * padding)

            # Wrap text
            wrapped_lines = self._wrap_text(text, effective_width, font)

            # Calculate text block dimensions
            ascent, descent = font.getmetrics()
            line_height = ascent + descent + font_size // 5
            total_text_height = len(wrapped_lines) * line_height

            # Calculate vertical starting position
            y_start = y + (max_height - total_text_height) // 2

            # Draw text
            current_y = y_start
            for line in wrapped_lines:
                # Center each line horizontally
                bbox = font.getbbox(line)
                line_width = bbox[2] - bbox[0]
                line_x = x + (max_width - line_width) // 2
                
                # Draw text with stroke
                draw.text(
                    (line_x, current_y), 
                    line, 
                    font=font, 
                    fill=text_color,
                    stroke_width=stroke_width,
                    stroke_fill=outline_color
                )
                
                current_y += line_height
            # print("Done drawing", image)

            return image
        except Exception as e:
            logging.error(f"An error occurred while adding text overlay: {e}")
            raise

    def add_multiple_texts(self, image_path: str | Image.Image | io.BytesIO, annotations: list) -> io.BytesIO:
        """
        Add multiple text overlays to an image.

        Args:
            image_path (str | Image.Image | io.BytesIO): Path to the input image or PIL Image object
            annotations (list): List of annotation dictionaries

        Returns:
            PIL.Image: Modified image with all text overlays
        """
        # print(image_path)
        # print(type(image_path))
        # print image instance

        try:
            if isinstance(image_path, str):
                image = Image.open(image_path).convert('RGBA')
            elif isinstance(image_path, io.BytesIO):
                image_path.seek(0)
                image = Image.open(image_path).convert('RGBA')
                image.format = 'JPEG'
            else:
                image = image_path

            # print(f"Image format: {image.format}, Size: {image.size}")
            print(image)

            for annotation in annotations:
                image = self.add_text(image, annotation)

            image = image.convert('RGB')

            # Save to buffer
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=95)
            output.seek(0)
            return output

        except Exception as e:
            logging.error(f"An error occurred while adding text overlays: {e}")
            raise 