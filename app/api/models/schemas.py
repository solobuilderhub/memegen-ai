from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

# API Key schemas
class ApiKeyStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"

class ApiKeyCreate(BaseModel):
    name: str
    permissions: List[str] = Field(default_factory=list)

class ApiKey(ApiKeyCreate):
    key_id: str
    hashed_key: str
    status: ApiKeyStatus
    created_at: datetime
    last_used: Optional[datetime] = None
    created_by: Optional[str] = None

# Meme API schemas
class MemeRequest(BaseModel):
    query: str

class TextPosition(BaseModel):
    x: int
    y: int
    text: str
    font_size: int

class MemeResponse(BaseModel):
    url: str
    presigned_url: str
    expiry_date: str

class TextBox(BaseModel):
    x: int
    y: int
    width: int
    height: int
    text: str
    font_size: int
    color: str  # HEX color
    style: str  # 'default', 'bold', 'comic', 'gradient'

## meme template schemas
class Font(BaseModel):
    size_range: str


class Annotation(BaseModel):
    name: str
    x: int
    y: int
    width: int
    height: int
    padding: int
    font: Font

class Source(BaseModel):
    name: str
    url: str
    width: int
    height: int
    box_count: int

class MemeTemplate(BaseModel):
    src: Source
    annotations: List[Annotation]

class MemeTemplateResponse(BaseModel):
    id: str
    src: Source
    annotations: List[Annotation]

class MemeTemplateUpdate(BaseModel):
    src: Optional[Source] = None
    annotations: Optional[List[Annotation]] = None