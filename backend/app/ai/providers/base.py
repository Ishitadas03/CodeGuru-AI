from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional


class AbstractAIProvider(ABC):
    """Abstract Base Class defining the contract for AI text generation models."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a complete, non-streaming string response.
        
        Args:
            prompt: User message prompt.
            system_instruction: Core directive instructions for the LLM.
            schema: Optional JSON schema dictionary to enforce structured outputs.
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks asynchronously.
        
        Args:
            prompt: User message prompt.
            system_instruction: Core directive instructions for the LLM.
        """
        pass
