# backend/app/api/deps.py
"""API dependencies wrapper forwarding to core dependencies to avoid duplication."""

from app.core.dependencies import (
    get_db,
    get_redis,
    get_current_user,
    get_current_active_user,
    get_admin_user,
    require_subscription,
    check_usage_quota,
    increment_usage
)
