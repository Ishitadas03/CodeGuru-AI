import uuid
import logging
from datetime import datetime, timedelta, date, timezone
from typing import Dict, List, Set, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dsa_progress import UserProblemProgress
from app.models.review import CodeReview
from app.repositories.dsa_progress_repo import DSAProgressRepository
from app.repositories.review_repo import ReviewRepository

from app.services.dsa_service import DSA_PROBLEMS
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    DsaStatsSchema,
    ReviewStatsSchema,
    StreakSchema,
    HeatmapBlockSchema,
    IssueCategoryCountSchema,
    ScoreHistorySchema
)


logger = logging.getLogger("codeguru")


class AnalyticsService:
    """Service responsible for aggregating user study metrics, streaks, and review scores."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.dsa_repo = DSAProgressRepository(db)
        self.review_repo = ReviewRepository(db)

    async def get_overview(self, user_id: uuid.UUID) -> AnalyticsOverviewResponse:
        """Fetch and aggregate all learning metrics for a specific user."""
        try:
            # 1. Fetch data from DB
            dsa_progress = await self.dsa_repo.get_user_progress(user_id)
            reviews = await self.review_repo.get_all_reviews_by_user(user_id)

            # 2. Gather distinct dates of activity for streaks
            activity_dates: Set[date] = set()
            for progress in dsa_progress:
                if progress.last_attempted_at:
                    activity_dates.add(progress.last_attempted_at.date())
                elif progress.solved_at:
                    activity_dates.add(progress.solved_at.date())

            for review in reviews:
                if review.created_at:
                    activity_dates.add(review.created_at.date())

            current_streak, longest_streak = self._calculate_streaks(activity_dates)

            # 3. Aggregate DSA Stats
            dsa_stats = self._aggregate_dsa_stats(dsa_progress)

            # 4. Aggregate Review Stats
            review_stats = self._aggregate_review_stats(reviews)

            # 5. Build Activity Heatmap for the last 365 days
            heatmap = self._generate_heatmap(reviews, dsa_progress)

            return AnalyticsOverviewResponse(
                dsa_stats=dsa_stats,
                review_stats=review_stats,
                streak=StreakSchema(
                    current_streak=current_streak,
                    longest_streak=longest_streak
                ),
                heatmap=heatmap
            )
        except Exception as e:
            logger.error(f"Failed to generate learning analytics overview: {str(e)}", exc_info=True)
            # Return empty response in case of failure, preventing complete app crash
            return AnalyticsOverviewResponse(
                dsa_stats=DsaStatsSchema(),
                review_stats=ReviewStatsSchema(),
                streak=StreakSchema(current_streak=0, longest_streak=0),
                heatmap=[]
            )

    def _calculate_streaks(self, activity_dates: Set[date]) -> Tuple[int, int]:
        """Compute current and longest daily active coding streaks in UTC dates."""
        if not activity_dates:
            return 0, 0

        sorted_dates = sorted(list(activity_dates), reverse=True)
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        # 1. Calculate current streak
        current_streak = 0
        if sorted_dates[0] == today:
            current_streak = 1
            expected_date = today - timedelta(days=1)
            for d in sorted_dates[1:]:
                if d == expected_date:
                    current_streak += 1
                    expected_date -= timedelta(days=1)
                elif d > expected_date:
                    continue
                else:
                    break
        elif sorted_dates[0] == yesterday:
            current_streak = 1
            expected_date = yesterday - timedelta(days=1)
            for d in sorted_dates[1:]:
                if d == expected_date:
                    current_streak += 1
                    expected_date -= timedelta(days=1)
                elif d > expected_date:
                    continue
                else:
                    break
        else:
            current_streak = 0

        # 2. Calculate longest streak
        sorted_dates_asc = sorted(list(activity_dates))
        longest_streak = 0
        temp_streak = 0
        prev_date = None

        for d in sorted_dates_asc:
            if prev_date is None:
                temp_streak = 1
            elif d == prev_date + timedelta(days=1):
                temp_streak += 1
            elif d == prev_date:
                continue
            else:
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                temp_streak = 1
            prev_date = d

        if temp_streak > longest_streak:
            longest_streak = temp_streak

        return current_streak, longest_streak

    def _aggregate_dsa_stats(self, dsa_progress: List[UserProblemProgress]) -> DsaStatsSchema:
        """Map DB progress records against static problems metadata."""
        solved_count = 0
        attempted_count = 0
        solved_by_difficulty = {"easy": 0, "medium": 0, "hard": 0}
        solved_by_topic: Dict[str, int] = {}

        # Build lookup table from static catalog
        catalog_lookup = {
            p["id"]: {"difficulty": p["difficulty"], "topic_slug": p["topic_slug"]}
            for p in DSA_PROBLEMS
        }

        for progress in dsa_progress:
            if progress.status == "solved":
                solved_count += 1
                meta = catalog_lookup.get(progress.problem_id)
                if meta:
                    diff = meta["difficulty"]
                    topic = meta["topic_slug"]
                    solved_by_difficulty[diff] = solved_by_difficulty.get(diff, 0) + 1
                    solved_by_topic[topic] = solved_by_topic.get(topic, 0) + 1
            elif progress.status == "attempted":
                # Ensure we don't count it if they solved it later
                already_solved = any(
                    p.problem_id == progress.problem_id and p.status == "solved"
                    for p in dsa_progress
                )
                if not already_solved:
                    attempted_count += 1

        return DsaStatsSchema(
            total_solved=solved_count,
            total_attempted=attempted_count,
            solved_by_difficulty=solved_by_difficulty,
            solved_by_topic=solved_by_topic
        )

    def _aggregate_review_stats(self, reviews: List[CodeReview]) -> ReviewStatsSchema:
        """Calculate review counts, averages, score histories, and common issues."""
        total_reviews = len(reviews)
        if total_reviews == 0:
            return ReviewStatsSchema()

        avg_score = sum(r.score for r in reviews) / total_reviews

        # Issues category counting
        issue_counts: Dict[str, int] = {}
        for r in reviews:
            for issue in r.issues:
                cat = issue.get("category", "general").lower()
                issue_counts[cat] = issue_counts.get(cat, 0) + 1

        common_issues = [
            IssueCategoryCountSchema(category=k, count=v)
            for k, v in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        score_history = [
            ScoreHistorySchema(
                date=r.created_at.date().isoformat() if r.created_at else datetime.now(timezone.utc).date().isoformat(),
                score=r.score
            )
            for r in reviews
        ]

        return ReviewStatsSchema(
            total_reviews=total_reviews,
            average_score=round(avg_score, 1),
            common_issues=common_issues,
            score_history=score_history
        )

    def _generate_heatmap(
        self,
        reviews: List[CodeReview],
        dsa_progress: List[UserProblemProgress]
    ) -> List[HeatmapBlockSchema]:
        """Aggregate all user activities into a 365-day time series."""
        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=365)

        heatmap_dict: Dict[str, int] = {}
        curr = start_date
        while curr <= today:
            heatmap_dict[curr.isoformat()] = 0
            curr += timedelta(days=1)

        # Increment counts
        for r in reviews:
            if r.created_at:
                d_str = r.created_at.date().isoformat()
                if d_str in heatmap_dict:
                    heatmap_dict[d_str] += 1

        for progress in dsa_progress:
            if progress.last_attempted_at:
                d_str = progress.last_attempted_at.date().isoformat()
                if d_str in heatmap_dict:
                    heatmap_dict[d_str] += 1

        return [
            HeatmapBlockSchema(date=k, count=v)
            for k, v in heatmap_dict.items()
        ]
