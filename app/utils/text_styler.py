from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict


class TextStyler:
    def __init__(self):
        # Ensure the font is downloaded and get its path
        self.font_path = "Anton-Regular.ttf"  # Using Anton as a free alternative
    
    def create_text_layer(self, image_size: Tuple[int, int], text_box: Dict) -> Image.Image:
        """
        Create a text layer with the specified styling.
        """
        layer = Image.new('RGBA', image_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        # Extract text box details
        text = text_box['text']
        x, y, width, height = text_box['x'], text_box['y'], text_box['width'], text_box['height']
        font_size = text_box.get('font_size', 36)
        color = text_box.get('color', '#FFFFFF')
        style = text_box.get('style', 'default')

        # Load font
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
            print(f"Failed to load font at {self.font_path}. Using default font.")

        # Fit text within the bounding box
        wrapped_text = self.wrap_text(text, font, width - 20, draw)  # 10px padding on each side

        # Calculate text size using textbbox for accurate measurement
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=4)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position to center the text within the bounding box
        text_x = x + (width - text_width) / 2
        text_y = y + (height - text_height) / 2

        # Apply text styles
        text_color = self.hex_to_rgb(color)
        if style == 'bold':
            font = self.make_bold(font)
        elif style == 'comic':
            font = self.get_comic_font(font_size)
        elif style == 'gradient':
            # Gradient will be applied after text is drawn
            pass

        # Draw text with outline for better readability
        self.draw_text_with_outline(draw, (text_x, text_y), wrapped_text, font, text_color)

        # Apply gradient if needed
        if style == 'gradient':
            layer = self.apply_gradient(layer, (text_x, text_y, text_width, text_height))

        return layer

    def wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> str:
        """
        Wrap text to fit within the max_width.
        """
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font, spacing=4)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:  # Avoid empty lines
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return "\n".join(lines)

    def draw_text_with_outline(self, draw: ImageDraw.Draw, position: Tuple[float, float], text: str, font: ImageFont.FreeTypeFont, fill: Tuple[int, int, int]):
        """
        Draw text with a black outline to enhance readability.
        """
        x, y = position
        outline_range = 2
        # Draw outline
        for dx in range(-outline_range, outline_range + 1):
            for dy in range(-outline_range, outline_range + 1):
                if dx != 0 or dy != 0:
                    draw.multiline_text((x + dx, y + dy), text, font=font, fill=(0, 0, 0))
        # Draw main text
        draw.multiline_text(position, text, font=font, fill=fill)

    def apply_gradient(self, layer: Image.Image, text_area: Tuple[float, float, float, float]) -> Image.Image:
        """
        Apply a vertical gradient to the specified text area.
        """
        x, y, width, height = text_area
        gradient = Image.new('RGBA', (int(width), int(height)), color=0)
        grad_draw = ImageDraw.Draw(gradient)

        for i in range(int(height)):
            ratio = i / height
            r = int(255 * ratio)
            g = int(255 * (1 - ratio))
            b = 150  # Fixed blueish component
            grad_draw.line([(0, i), (width, i)], fill=(r, g, b, 255))

        # Paste the gradient onto the layer
        layer.paste(gradient, (int(x), int(y)), gradient)
        return layer

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert HEX color to RGB tuple.
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def make_bold(self, font: ImageFont.FreeTypeFont) -> ImageFont.FreeTypeFont:
        """
        Simulate bold by using a slightly larger font or a different weight if available.
        """
        try:
            bold_font_path = self.font_path.replace('.ttf', 'bd.ttf')
            return ImageFont.truetype(bold_font_path, font.size)
        except IOError:
            # If bold font not available, return the original font
            return font

    def get_comic_font(self, font_size: int) -> ImageFont.FreeTypeFont:
        """
        Load a comic-style font.
        """
        try:
            # Ensure a comic font is downloaded and available
            comic_font_path = "Comic-Regular.ttf"
            return ImageFont.truetype(comic_font_path, font_size)
        except IOError:
            # Fallback to default font
            return ImageFont.load_default()