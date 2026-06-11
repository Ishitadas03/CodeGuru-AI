from fastapi import APIRouter
from app.api.v1 import auth, users, reviews, dsa, analytics, interview, coordinator, admin, chat, billing

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(dsa.router, prefix="/dsa", tags=["dsa"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(coordinator.router, prefix="/coordinator", tags=["coordinator"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])




