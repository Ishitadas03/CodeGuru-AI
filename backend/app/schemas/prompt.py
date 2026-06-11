import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PromptVersionBase(BaseModel):
    name: str = Field(..., max_length=100)
    version: str = Field(..., max_length=20)
    content: str


class PromptVersionCreate(PromptVersionBase):
    is_active: bool = True


class PromptVersionResponse(PromptVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    thumbs_up: int
    thumbs_down: int
    performance_score: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PromptFeedbackRequest(BaseModel):
    is_thumbs_up: bool
