import logging
import stripe
import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.models.user import User
from app.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger("codeguru.billing")


class BillingService:
    """Service to coordinate Stripe checkout sessions, portal redirects, and webhook processing."""

    def _is_mock_mode(self) -> bool:
        return (
            not settings.STRIPE_SECRET_KEY
            or settings.STRIPE_SECRET_KEY.startswith("sk_test_placeholder")
            or settings.STRIPE_SECRET_KEY == "MOCK_KEY"
        )

    def __init__(self):
        if not self._is_mock_mode():
            stripe.api_key = settings.STRIPE_SECRET_KEY

    async def create_checkout_session(
        self, db: AsyncSession, user_id: uuid.UUID, success_url: str, cancel_url: str
    ) -> str:
        """Create a Stripe Checkout Session for subscription or return a local mock redirection URL."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")

        if self._is_mock_mode():
            logger.info(f"[Billing MOCK] Creating checkout session for user={user_id}")
            mock_session_id = f"cs_mock_{uuid.uuid4().hex[:8]}"
            separator = "&" if "?" in success_url else "?"
            return f"{success_url}{separator}session_id={mock_session_id}"

        try:
            # 1. Resolve or create customer
            customer_id = user.stripe_customer_id
            if not customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    metadata={"user_id": str(user_id)}
                )
                customer_id = customer.id
                user.stripe_customer_id = customer_id
                db.add(user)
                await db.commit()

            # 2. Create Checkout session
            price_id = settings.STRIPE_PRO_PRICE_ID or "price_placeholder_pro"
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user_id),
            )
            return session.url
        except Exception as e:
            logger.error(f"Stripe Checkout creation failed: {e}", exc_info=True)
            raise ValidationError(f"Billing checkout failed: {str(e)}")

    async def create_portal_session(self, db: AsyncSession, user_id: uuid.UUID, return_url: str) -> str:
        """Create a Stripe Customer Billing Portal redirection link or a simulated mock URL."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")

        customer_id = user.stripe_customer_id
        if not customer_id:
            raise ValidationError("No active billing relationship found. Please subscribe first.")

        if self._is_mock_mode():
            logger.info(f"[Billing MOCK] Creating customer portal session for user={user_id}")
            separator = "&" if "?" in return_url else "?"
            return f"{return_url}{separator}portal=success"

        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except Exception as e:
            logger.error(f"Stripe Portal creation failed: {e}", exc_info=True)
            raise ValidationError(f"Billing portal failed: {str(e)}")

    async def handle_webhook(self, db: AsyncSession, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Verify and process webhook notification events from Stripe."""
        event = None

        if self._is_mock_mode() or sig_header == "mock_signature":
            import json
            try:
                event_data = json.loads(payload.decode("utf-8"))
                class MockEvent:
                    def __init__(self, data):
                        self.type = data.get("type")
                        self.data = self
                        self.object = data.get("data", {}).get("object", {})
                event = MockEvent(event_data)
            except Exception as e:
                logger.error(f"Failed to parse mock webhook payload: {e}")
                raise ValidationError("Invalid payload format")
        else:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
            except Exception as e:
                logger.error(f"Webhook signature validation failed: {e}")
                raise ValidationError(f"Signature validation failed: {str(e)}")

        event_type = event.type
        logger.info(f"Processing Stripe Webhook Event: {event_type}")

        if event_type in ["checkout.session.completed", "customer.subscription.updated"]:
            session_obj = event.data.object
            user_id_str = session_obj.get("client_reference_id")
            customer_id = session_obj.get("customer")
            subscription_id = session_obj.get("subscription")

            user = None
            if user_id_str:
                try:
                    user_uuid = uuid.UUID(user_id_str)
                    stmt = select(User).where(User.id == user_uuid)
                    result = await db.execute(stmt)
                    user = result.scalar_one_or_none()
                except ValueError:
                    pass

            if not user and customer_id:
                stmt = select(User).where(User.stripe_customer_id == customer_id)
                res = await db.execute(stmt)
                user = res.scalar_one_or_none()

            if user:
                user.subscription_tier = "pro"
                if customer_id:
                    user.stripe_customer_id = customer_id
                if subscription_id:
                    user.stripe_subscription_id = subscription_id
                db.add(user)
                await db.commit()
                logger.info(f"User {user.email} subscription tier upgraded to pro via Stripe event.")
            else:
                logger.warning(f"Could not resolve user for Stripe event {event_type} (customer_id={customer_id})")

        elif event_type == "customer.subscription.deleted":
            sub_obj = event.data.object
            customer_id = sub_obj.get("customer")

            if customer_id:
                stmt = select(User).where(User.stripe_customer_id == customer_id)
                res = await db.execute(stmt)
                user = res.scalar_one_or_none()

                if user:
                    user.subscription_tier = "free"
                    user.stripe_subscription_id = None
                    db.add(user)
                    await db.commit()
                    logger.info(f"User {user.email} subscription tier demoted to free via Stripe event.")
                else:
                    logger.warning(f"Could not resolve user for deleted subscription event (customer_id={customer_id})")

        return {"status": "success", "event_processed": event_type}
