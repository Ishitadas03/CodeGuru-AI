from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TopicResponse(BaseModel):
    """Schema representing a DSA Topic category (e.g. Arrays, Trees)."""
    id: str = Field(..., description="Unique slug or string ID of the topic.")
    name: str = Field(..., description="Human-readable name of the topic.")
    slug: str
    description: str


class ProblemResponse(BaseModel):
    """Schema representing a single coding challenge problem definition."""
    id: str = Field(..., description="Unique slug or ID of the coding challenge.")
    topic_slug: str
    title: str = Field(..., description="Title of the challenge (e.g., Two Sum).")
    difficulty: str = Field(..., description="Difficulty level (easy, medium, hard).")
    description: str = Field(..., description="Problem description body in markdown format.")
    starter_code: Dict[str, str] = Field(
        ...,
        description="Key-value dictionary mapping languages to their starting codes."
    )


class DryRunStepSchema(BaseModel):
    """Schema detailing a single simulated step trace in a code dry run."""
    step: int
    line_number: int
    description: str
    variables_state: str


class ComplexitySchema(BaseModel):
    """Schema detailing Big-O notation complexities and text explanations."""
    time_complexity: str
    time_explanation: str
    space_complexity: str
    space_explanation: str


class ExplanationResponse(BaseModel):
    """Full serialized output schema representing an interactive concept explanation."""
    concept_name: str
    explanation: str
    complexity: ComplexitySchema
    dry_run: List[DryRunStepSchema]


class ExplainRequest(BaseModel):
    """Request schema for asking the Teacher Agent to explain code for a problem."""
    code: str
    language: str
