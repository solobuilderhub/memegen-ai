import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.services.api_key_service import ApiKeyService
from app.api.models.schemas import ApiKeyCreate
from datetime import datetime, timedelta
from dotenv import load_dotenv

def create_initial_admin_key():
    # Load environment variables
    load_dotenv()
    
    try:
        service = ApiKeyService()
        key_data = ApiKeyCreate(
            name="Initial Admin Key",
            permissions=["admin", "generate_meme"]
        )
        raw_key, key_info = service.create_api_key(key_data)
        
        print("\n=== API Key Created Successfully ===")
        print(f"API Key: {raw_key}")
        print("IMPORTANT: Save this key! It won't be shown again.")
        print(f"Key ID: {key_info.key_id}")
        print(f"Name: {key_info.name}")
        print(f"Permissions: {', '.join(key_info.permissions)}")
        print(f"Expires: {key_info.expires_at}")
        print("===================================\n")
        
    except Exception as e:
        print(f"Error creating admin key: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_initial_admin_key()