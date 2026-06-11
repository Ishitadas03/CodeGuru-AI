import logging
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prompt import PromptVersion

# Import prompt defaults
from app.ai.prompts.review_prompts import (
    REVIEWER_SYSTEM_INSTRUCTION,
    REVIEWER_USER_PROMPT,
    DEBUGGER_SYSTEM_INSTRUCTION,
    DEBUGGER_USER_PROMPT,
)
from app.ai.prompts.coordinator_prompts import (
    COORDINATOR_SYSTEM_INSTRUCTION,
    COORDINATOR_USER_PROMPT,
)
from app.ai.prompts.dsa_prompts import (
    DSA_SYSTEM_INSTRUCTION,
    DSA_EXPLAIN_PROMPT,
)
from app.ai.prompts.interview_prompts import (
    INTERVIEW_SYSTEM_INSTRUCTION,
    INTERVIEW_EVAL_SYSTEM_INSTRUCTION,
    INTERVIEW_CHAT_PROMPT,
    INTERVIEW_EVAL_PROMPT,
)

logger = logging.getLogger("codeguru.prompt_service")

# Fallback defaults registry
DEFAULT_PROMPTS = {
    "reviewer_system": REVIEWER_SYSTEM_INSTRUCTION,
    "reviewer_user": REVIEWER_USER_PROMPT,
    "debugger_system": DEBUGGER_SYSTEM_INSTRUCTION,
    "debugger_user": DEBUGGER_USER_PROMPT,
    "coordinator_system": COORDINATOR_SYSTEM_INSTRUCTION,
    "coordinator_user": COORDINATOR_USER_PROMPT,
    "dsa_system": DSA_SYSTEM_INSTRUCTION,
    "dsa_explain": DSA_EXPLAIN_PROMPT,
    "interview_system": INTERVIEW_SYSTEM_INSTRUCTION,
    "interview_eval_system": INTERVIEW_EVAL_SYSTEM_INSTRUCTION,
    "interview_chat": INTERVIEW_CHAT_PROMPT,
    "interview_eval": INTERVIEW_EVAL_PROMPT,
}


class PromptService:
    """Manages system instruction prompts, loading them from DB or falling back to code registry."""

    async def get_prompt(
        self,
        db: Optional[AsyncSession],
        name: str
    ) -> Tuple[str, str]:
        """Fetch active prompt template from database. Falls back to static defaults if missing or error."""
        if db:
            try:
                stmt = select(PromptVersion).where(
                    PromptVersion.name == name,
                    PromptVersion.is_active == True
                ).order_by(PromptVersion.version.desc())
                res = await db.execute(stmt)
                prompt_version = res.scalar()
                if prompt_version:
                    return prompt_version.content, prompt_version.version
            except Exception as e:
                logger.warning(f"Database unavailable to fetch prompt '{name}': {str(e)}")

        default_prompt = DEFAULT_PROMPTS.get(name, "")
        return default_prompt, "default"

    async def record_feedback(
        self,
        db: AsyncSession,
        name: str,
        version: str,
        is_thumbs_up: bool
    ) -> None:
        """Increment thumbs up/down counters and update the performance score of a prompt."""
        try:
            stmt = select(PromptVersion).where(
                PromptVersion.name == name,
                PromptVersion.version == version
            )
            res = await db.execute(stmt)
            prompt_version = res.scalar()
            
            if prompt_version:
                if is_thumbs_up:
                    prompt_version.thumbs_up += 1
                else:
                    prompt_version.thumbs_down += 1
                
                total = prompt_version.thumbs_up + prompt_version.thumbs_down
                if total > 0:
                    prompt_version.performance_score = float(prompt_version.thumbs_up) / total
                await db.flush()
        except Exception as e:
            logger.error(f"Failed to record prompt feedback for {name} ({version}): {str(e)}")
