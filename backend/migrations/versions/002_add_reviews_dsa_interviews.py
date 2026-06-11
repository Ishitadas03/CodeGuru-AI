"""add reviews dsa interviews

Revision ID: 002_add_reviews_dsa_interviews
Revises: 001_initial_schema
Create Date: 2026-06-07 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision: str = "002_add_reviews_dsa_interviews"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create submissions table
    op.create_table(
        "submissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_submissions_user_id"), "submissions", ["user_id"], unique=False)

    # 2. Create code_reviews table
    op.create_table(
        "code_reviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("issues", sa.JSON(), nullable=False),
        sa.Column("refactored_code", sa.Text(), nullable=False),
        sa.Column("has_bugs", sa.Boolean(), nullable=False),
        sa.Column("bugs", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_code_reviews_submission_id"), "code_reviews", ["submission_id"], unique=False)

    # 3. Create user_problem_progress table
    op.create_table(
        "user_problem_progress",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("problem_id", sa.String(length=100), nullable=False),
        sa.Column("topic_slug", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("solved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_attempted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_user_problem_progress_user_id"), "user_problem_progress", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_problem_progress_problem_id"), "user_problem_progress", ["problem_id"], unique=False)
    op.create_index(op.f("ix_user_problem_progress_topic_slug"), "user_problem_progress", ["topic_slug"], unique=False)

    # 4. Create interview_sessions table
    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=False),
        sa.Column("messages", sa.JSON(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("feedback", sa.JSON(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_interview_sessions_user_id"), "interview_sessions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_interview_sessions_user_id"), table_name="interview_sessions")
    op.drop_table("interview_sessions")

    op.drop_index(op.f("ix_user_problem_progress_topic_slug"), table_name="user_problem_progress")
    op.drop_index(op.f("ix_user_problem_progress_problem_id"), table_name="user_problem_progress")
    op.drop_index(op.f("ix_user_problem_progress_user_id"), table_name="user_problem_progress")
    op.drop_table("user_problem_progress")

    op.drop_index(op.f("ix_code_reviews_submission_id"), table_name="code_reviews")
    op.drop_table("code_reviews")

    op.drop_index(op.f("ix_submissions_user_id"), table_name="submissions")
    op.drop_table("submissions")
