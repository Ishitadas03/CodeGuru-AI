from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class DsaStatsSchema(BaseModel):
    """Schema representing DSA problems metrics aggregated by difficulty and topic."""
    total_solved: int = Field(0, description="Total number of solved DSA problems.")
    total_attempted: int = Field(0, description="Total number of attempted (but not solved) DSA problems.")
    solved_by_difficulty: Dict[str, int] = Field(
        default_factory=lambda: {"easy": 0, "medium": 0, "hard": 0},
        description="Solved problem counts grouped by easy, medium, and hard."
    )
    solved_by_topic: Dict[str, int] = Field(
        default_factory=dict,
        description="Solved problem counts grouped by topic slugs."
    )


class IssueCategoryCountSchema(BaseModel):
    """Schema representing count of code issues flagged for a category."""
    category: str
    count: int


class ScoreHistorySchema(BaseModel):
    """Schema representing a historical code review score."""
    date: str = Field(..., description="Date of review in YYYY-MM-DD format.")
    score: int


class ReviewStatsSchema(BaseModel):
    """Schema representing code review aggregates and trends."""
    total_reviews: int = Field(0, description="Total reviews requested.")
    average_score: float = Field(0.0, description="Average score across all code reviews.")
    common_issues: List[IssueCategoryCountSchema] = Field(
        default_factory=list,
        description="List of categories and their frequencies of issues flagged by AI."
    )
    score_history: List[ScoreHistorySchema] = Field(
        default_factory=list,
        description="Time series historical scores for line charts."
    )


class StreakSchema(BaseModel):
    """Schema tracking current and longest daily active coding streaks."""
    current_streak: int = Field(0, description="Current daily active streak in days.")
    longest_streak: int = Field(0, description="All-time longest daily active streak in days.")


class HeatmapBlockSchema(BaseModel):
    """Schema representing a single day in the GitHub-style contribution heatmap."""
    date: str = Field(..., description="Date in YYYY-MM-DD format.")
    count: int = Field(..., description="Total activities (submissions + reviews) completed on this day.")


class AnalyticsOverviewResponse(BaseModel):
    """Aggregated response containing overall learning statistics, graph logs, and streaks."""
    dsa_stats: DsaStatsSchema
    review_stats: ReviewStatsSchema
    streak: StreakSchema
    heatmap: List[HeatmapBlockSchema]


class DSAProgressUpdateRequest(BaseModel):
    """Request model to set or update DSA problem progress."""
    problem_id: str
    topic_slug: str
    status: str = Field(..., pattern="^(solved|attempted)$", description="Must be 'solved' or 'attempted'.")
    language: str
    code: str
