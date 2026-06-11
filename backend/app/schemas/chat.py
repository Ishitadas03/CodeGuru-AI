import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    """Schema representing uploaded document metadata."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str = Field(..., description="Uploaded PDF filename")
    file_size: int = Field(..., description="Size of file in bytes")
    num_chunks: int = Field(..., description="Number of parsed text chunks")
    created_at: datetime


class ChatSessionCreate(BaseModel):
    """Schema for initializing a new chat session."""
    title: Optional[str] = Field(None, max_length=255, description="Custom chat session title")


class ChatMessageResponse(BaseModel):
    """Schema representing a single message in a chat history."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Text content of the message")
    created_at: datetime


class ChatSessionResponse(BaseModel):
    """Schema representing a chat session details."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str = Field(..., description="Title of the session")
    created_at: datetime


class RAGMessageRequest(BaseModel):
    """Schema for posting a new message in a RAG session."""
    message: str = Field(..., min_length=1, description="Message text query to search and chat")


class SourceMetadataSchema(BaseModel):
    """Schema representing retrieved chunk source citation."""
    filename: str
    page: int
    score: float


class RAGQueryResponse(BaseModel):
    """Schema representing contextual response with source documents."""
    message: ChatMessageResponse
    sources: List[SourceMetadataSchema]
