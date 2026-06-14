import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


@pytest.fixture(autouse=True)
def mock_vector_db():
    """Mock VectorService to avoid requiring a live PostgreSQL connection in tests."""
    with patch("app.services.vector_service.VectorService.__init__") as mock_init, \
         patch("app.services.vector_service.VectorService.add_chunks", new_callable=AsyncMock) as mock_add, \
         patch("app.services.vector_service.VectorService.query_similar_chunks", new_callable=AsyncMock) as mock_query, \
         patch("app.services.vector_service.VectorService.delete_document_vectors", new_callable=AsyncMock) as mock_del:
        mock_init.return_value = None
        mock_query.return_value = []
        yield


@pytest.fixture(autouse=True)
def mock_embedding_generation():
    """Mock the BGE embedding calls to prevent live downloading and latency."""
    with patch("app.services.embedding_service.EmbeddingService.embed_query") as mock_eq, \
         patch("app.services.embedding_service.EmbeddingService.embed_documents") as mock_ed:
        mock_eq.return_value = [0.1] * 384
        mock_ed.return_value = [[0.1] * 384]
        yield mock_eq, mock_ed


@pytest.fixture
def mock_pdf_reader():
    """Mock pypdf reader to return structured pages."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "This is a document about python coding best practices. Keep methods small."
    
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    
    with patch("app.services.pdf_service.PdfReader", return_value=mock_reader) as mock:
        yield mock


@pytest.mark.asyncio
async def test_rag_document_lifecycle(client: AsyncClient, db: AsyncSession, mock_pdf_reader) -> None:
    """Verify document upload, listing, and deletion flow."""
    # 1. Register & login
    email = "rag_test@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "securepassword123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "securepassword123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload document
    pdf_content = b"%PDF-1.4 Mock PDF Content"
    files = {"file": ("test_doc.pdf", pdf_content, "application/pdf")}
    upload_res = await client.post(
        f"{settings.API_V1_STR}/chat/documents/upload",
        files=files,
        headers=headers
    )
    assert upload_res.status_code == 201
    doc_data = upload_res.json()
    assert doc_data["filename"] == "test_doc.pdf"
    assert doc_data["num_chunks"] > 0
    doc_id = doc_data["id"]

    # 3. List documents
    list_res = await client.get(f"{settings.API_V1_STR}/chat/documents", headers=headers)
    assert list_res.status_code == 200
    docs = list_res.json()
    assert len(docs) == 1
    assert docs[0]["id"] == doc_id

    # 4. Delete document
    del_res = await client.delete(f"{settings.API_V1_STR}/chat/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 204

    # 5. Verify document is gone
    list_res = await client.get(f"{settings.API_V1_STR}/chat/documents", headers=headers)
    assert len(list_res.json()) == 0


@pytest.mark.asyncio
async def test_rag_chat_flow(client: AsyncClient, db: AsyncSession, mock_pdf_reader) -> None:
    """Verify chat session creation, message sending, retrieval context grounding, and history."""
    # 1. Register & login
    email = "rag_chat@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "securepassword123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "securepassword123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload document
    pdf_content = b"%PDF-1.4 Mock PDF Content"
    files = {"file": ("coding_standards.pdf", pdf_content, "application/pdf")}
    await client.post(
        f"{settings.API_V1_STR}/chat/documents/upload",
        files=files,
        headers=headers
    )

    # 3. Create chat session
    session_res = await client.post(
        f"{settings.API_V1_STR}/chat/sessions",
        json={"title": "Test Chat"},
        headers=headers
    )
    assert session_res.status_code == 201
    session_data = session_res.json()
    session_id = session_data["id"]
    assert session_data["title"] == "Test Chat"

    # 4. Query chat (RAG grounded response)
    mock_llm_response = "According to coding_standards.pdf, you should keep python methods small for readability."
    
    with patch("app.ai.router.AIRouter.generate_with_fallback", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = (mock_llm_response, "gemini-2.5-pro")

        query_res = await client.post(
            f"{settings.API_V1_STR}/chat/sessions/{session_id}/message",
            json={"message": "What does the document say about method sizes?"},
            headers=headers
        )
        assert query_res.status_code == 200
        query_data = query_res.json()
        assert query_data["message"]["role"] == "assistant"
        assert query_data["message"]["content"] == mock_llm_response
        assert len(query_data["sources"]) > 0
        assert query_data["sources"][0]["filename"] == "coding_standards.pdf"

    # 5. Fetch chat message history
    history_res = await client.get(
        f"{settings.API_V1_STR}/chat/sessions/{session_id}/messages",
        headers=headers
    )
    assert history_res.status_code == 200
    messages = history_res.json()
    assert len(messages) == 2  # User query + Assistant response
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What does the document say about method sizes?"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == mock_llm_response
