# app/utils/font_utils.py

import os
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Available fonts
AVAILABLE_FONTS = {
    "Anton-Regular.ttf",
    "ComicSansMS.ttf",
    "Roboto-Regular.ttf",
    "Impact.ttf",
    "Arial.ttf"
}

DEFAULT_FONT = "Arial.ttf"

def get_font_path(font_name: str = DEFAULT_FONT) -> str:
    """
    Gets the path for the requested font if available, otherwise returns default font path.

    Args:
        font_name (str): Name of the font file (e.g., "Anton-Regular.ttf")
    
    Returns:
        str: Path to the font file
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(current_dir, 'fonts')
    
    # If font name not provided or not in available fonts, use default
    if not font_name or font_name not in AVAILABLE_FONTS:
        logger.warning(f"Font '{font_name}' not available. Using default font: {DEFAULT_FONT}")
        font_name = DEFAULT_FONT

    font_path = os.path.join(fonts_dir, font_name)
    
    # Check if font exists
    if not os.path.isfile(font_path):
        logger.warning(f"Font file not found at {font_path}. Using default font: {DEFAULT_FONT}")
        font_path = os.path.join(fonts_dir, DEFAULT_FONT)
        
        # If even default font doesn't exist, raise error
        if not os.path.isfile(font_path):
            raise FileNotFoundError(f"Default font not found at {font_path}")

    logger.info(f"Using font: {font_path}")
    return font_path

def list_available_fonts() -> list:
    """
    Lists all available fonts.

    Returns:
        list: List of available font names
    """
    return sorted(list(AVAILABLE_FONTS))

