import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.rag_repo import RAGRepository
from app.services.rag_service import RAGService
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.schemas.chat import (
    DocumentResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
    RAGMessageRequest,
    RAGQueryResponse
)

router = APIRouter()
rag_service = RAGService()


@router.post("/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Upload a PDF document, extract and chunk text, compute BGE embeddings, and index in ChromaDB."""
    if not file.filename.lower().endswith(".pdf"):
        raise ValidationError("Only PDF files are supported.")

    file_bytes = await file.read()
    try:
        doc = await rag_service.upload_document(
            db,
            user_id=current_user.id,
            filename=file.filename,
            file_bytes=file_bytes
        )
        return doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[DocumentResponse]:
    """List all documents uploaded by the current user."""
    repo = RAGRepository(db)
    docs = await repo.get_user_documents(current_user.id)
    return docs


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete document metadata and remove indexed vectors from ChromaDB."""
    success = await rag_service.delete_document(
        db,
        user_id=current_user.id,
        document_id=document_id
    )
    if not success:
        raise NotFoundError("Document not found or access denied.")


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ChatSessionResponse:
    """Initialize a new RAG chat session."""
    repo = RAGRepository(db)
    title = payload.title or "New Chat"
    session = await repo.create_chat_session(user_id=current_user.id, title=title)
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ChatSessionResponse]:
    """Retrieve all chat sessions for the current user."""
    repo = RAGRepository(db)
    sessions = await repo.get_user_chat_sessions(current_user.id)
    return sessions


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ChatMessageResponse]:
    """Fetch all messages in a chat session chronologically, enforcing ownership boundaries."""
    repo = RAGRepository(db)
    session = await repo.get_chat_session(session_id)
    if not session:
        raise NotFoundError("Chat session not found.")
    if session.user_id != current_user.id:
        raise ForbiddenError("Access denied to this chat session.")

    messages = await repo.get_session_messages(session_id)
    return messages


@router.post("/sessions/{session_id}/message", response_model=RAGQueryResponse)
async def post_chat_message(
    session_id: uuid.UUID,
    payload: RAGMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> RAGQueryResponse:
    """Submit a query in a session, perform similarity search on ChromaDB, and generate grounded answer."""
    try:
        msg, sources = await rag_service.query_chat(
            db,
            user_id=current_user.id,
            session_id=session_id,
            message_content=payload.message
        )
        return RAGQueryResponse(message=msg, sources=sources)
    except PermissionError as e:
        raise ForbiddenError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
