from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    azure_openai_api_key: str
    azure_openai_api_version: str
    azure_openai_api_endpoint: str
    azure_openai_api_deployment_name: str 
    aws_access_key: str
    aws_secret_key: str
    aws_region: str
    s3_bucket_name: str
    mongo_uri: str
    rate_limit_calls: int = 100  # calls per window
    rate_limit_window: int = 3600

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    print("Initializing settings...")
    return Settings()