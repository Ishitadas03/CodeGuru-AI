import uuid
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.agents.coordinator_agent import CoordinatorAgent
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.core.config import settings
from app.core.exceptions import ValidationError

logger = logging.getLogger("codeguru")

router = APIRouter()


class CoordinatorRequest(BaseModel):
    user_input: str
    session_id: Optional[uuid.UUID] = None


class CoordinatorResponse(BaseModel):
    intent: str
    reasoning: str
    response: str
    data: Dict[str, Any]


def get_ai_provider():
    """Resolve AI Provider dynamically: OpenAI if key is set, else local Ollama."""
    if (
        settings.OPENAI_API_KEY
        and not settings.OPENAI_API_KEY.startswith("sk-proj-xxxx")
        and settings.OPENAI_API_KEY != "MOCK_KEY"
        and settings.OPENAI_API_KEY.strip()
    ):
        return OpenAIProvider(model="gpt-4o-mini")
    else:
        return OllamaProvider(model="codellama")


@router.post(
    "/route",
    response_model=CoordinatorResponse,
    status_code=status.HTTP_200_OK,
    summary="Route user input to target agent and execute"
)
async def route_user_query(
    payload: CoordinatorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CoordinatorResponse:
    """Analyze query, decide the agent intent, run target execution, and return results."""
    if not payload.user_input.strip():
        raise ValidationError("Input query cannot be empty.")

    provider = get_ai_provider()
    coordinator = CoordinatorAgent(provider)

    try:
        result = await coordinator.route_and_execute(
            user_input=payload.user_input,
            user_id=current_user.id,
            db=db,
            session_id=payload.session_id
        )
        return CoordinatorResponse(**result)
    except Exception as e:
        logger.error(f"Coordinator route execution crashed: {str(e)}", exc_info=True)
        return CoordinatorResponse(
            intent="general",
            reasoning=f"System error: {str(e)}",
            response="I encountered an internal error while routing your request. Please try again.",
            data={}
        )
