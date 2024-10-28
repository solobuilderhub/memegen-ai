# app/utils/font_utils.py

import os
import requests

def download_font(font_url: str, save_path: str):
    """
    Downloads a font from the specified URL and saves it to the given path.
    """
    response = requests.get(font_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Font downloaded and saved to {save_path}")
    else:
        raise Exception(f"Failed to download font from {font_url}")

def ensure_font(font_name: str = "Anton-Regular.ttf"):
    """
    Ensures that the specified font is available locally. If not, downloads it.
    """
    current_dir = os.path.dirname(__file__)
    fonts_dir = os.path.join(current_dir, 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    font_path = os.path.join(fonts_dir, font_name)
    
    if not os.path.isfile(font_path):
        # Download Anton from Google Fonts
        font_url = "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf"
        download_font(font_url, font_path)
    else:
        print(f"Font already exists at {font_path}")
    
    return font_path

def get_font_path(font_name: str):
    """
    Retrieves the font path from environment variables or uses bundled fonts.
    """
    env_var = f"FONT_{font_name.upper().replace('-', '_').replace('.ttf', '')}"
    font_path = os.getenv(env_var)
    
    if font_path and os.path.isfile(font_path):
        return font_path
    else:
        # Fallback to bundled fonts
        current_dir = os.path.dirname(__file__)
        fonts_dir = os.path.join(current_dir, 'fonts')
        bundled_font_path = os.path.join(fonts_dir, font_name)
        
        if not os.path.isfile(bundled_font_path):
            raise FileNotFoundError(f"Font not found at {bundled_font_path}")
        
        return bundled_font_path

def get_bundled_font(font_name: str):
    """
    Retrieves the path to a bundled font.
    """
    current_dir = os.path.dirname(__file__)
    fonts_dir = os.path.join(current_dir, 'fonts')
    font_path = os.path.join(fonts_dir, font_name)
    
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Bundled font not found at {font_path}")
    
    return font_path