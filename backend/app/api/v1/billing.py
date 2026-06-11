from fastapi import APIRouter, Depends, Request, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.billing import (
    CheckoutRequest,
    CheckoutResponse,
    PortalRequest,
    PortalResponse
)
from app.services.billing_service import BillingService
from typing import Optional

router = APIRouter()
billing_service = BillingService()


@router.post("/checkout", response_model=CheckoutResponse, status_code=status.HTTP_200_OK)
async def create_checkout_session(
    payload: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CheckoutResponse:
    """Initialize a Stripe Checkout Session for subscription upgrade."""
    checkout_url = await billing_service.create_checkout_session(
        db=db,
        user_id=current_user.id,
        success_url=payload.success_url,
        cancel_url=payload.cancel_url
    )
    return CheckoutResponse(checkout_url=checkout_url)


@router.post("/portal", response_model=PortalResponse, status_code=status.HTTP_200_OK)
async def create_portal_session(
    payload: PortalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortalResponse:
    """Initialize a Stripe Customer Portal redirect link to manage subscriptions."""
    portal_url = await billing_service.create_portal_session(
        db=db,
        user_id=current_user.id,
        return_url=payload.return_url
    )
    return PortalResponse(portal_url=portal_url)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Receive raw Stripe event webhook messages and perform fulfillment updates."""
    payload = await request.body()
    sig_header = stripe_signature or ""
    res = await billing_service.handle_webhook(
        db=db,
        payload=payload,
        sig_header=sig_header
    )
    return res
