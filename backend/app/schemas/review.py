import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ReviewRequest(BaseModel):
    """Schema for initiating a new code review request."""
    code: str = Field(..., min_length=1, max_length=100000, description="Code body to analyze.")
    language: str = Field(..., min_length=1, max_length=50, description="Programming language of the code.")


class IssueSchema(BaseModel):
    """Schema representing a single quality issue found in the code."""
    model_config = ConfigDict(from_attributes=True)

    category: str = Field(..., description="Classification category (e.g. security, performance).")
    line: int = Field(..., description="1-indexed line reference.")
    description: str = Field(..., description="Issue description details.")
    suggestion: str = Field(..., description="Actionable suggestion or fix.")


class BugSchema(BaseModel):
    """Schema representing a logical or compiler bug discovered in the code."""
    model_config = ConfigDict(from_attributes=True)

    line: int = Field(..., description="1-indexed line reference.")
    severity: str = Field(..., description="Severity classification (error or warning).")
    description: str = Field(..., description="Detailed bug description.")
    fix: str = Field(..., description="Code snippet demonstrating the fix.")


class AnalyzerReportSchema(BaseModel):
    """Schema representing generic static analyzer report output."""
    model_config = ConfigDict(from_attributes=True)

    analyzer: str
    supported: bool
    results: Dict[str, Any]


class StaticAnalysisResponse(BaseModel):
    """Schema representing aggregated static analysis reports for all tools."""
    model_config = ConfigDict(from_attributes=True)

    language: str
    treesitter: Optional[AnalyzerReportSchema] = None
    pylint: Optional[AnalyzerReportSchema] = None
    bandit: Optional[AnalyzerReportSchema] = None
    radon: Optional[AnalyzerReportSchema] = None


class ReviewResponse(BaseModel):
    """Full serialized output schema representing code review findings."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    submission_id: uuid.UUID
    score: int = Field(..., ge=0, le=100)
    summary: str
    issues: List[IssueSchema]
    refactored_code: str
    has_bugs: bool
    bugs: List[BugSchema]
    static_analysis: Optional[StaticAnalysisResponse] = None
    created_at: datetime


