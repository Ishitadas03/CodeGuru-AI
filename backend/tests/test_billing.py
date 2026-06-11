import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.models.user import User


@pytest.mark.asyncio
async def test_billing_checkout_success(client: AsyncClient, db: AsyncSession) -> None:
    """Verify that a user can successfully request a checkout redirect URL."""
    # 1. Register and login
    email = "subscriber@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "password123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Request checkout URL
    checkout_res = await client.post(
        f"{settings.API_V1_STR}/billing/checkout",
        json={
            "success_url": "http://localhost:3000/settings/billing/success",
            "cancel_url": "http://localhost:3000/settings/billing/cancel"
        },
        headers=headers
    )
    assert checkout_res.status_code == 200
    data = checkout_res.json()
    assert "checkout_url" in data
    assert "session_id=" in data["checkout_url"]


@pytest.mark.asyncio
async def test_billing_portal_lifecycle(client: AsyncClient, db: AsyncSession) -> None:
    """Verify portal fails if user has no Stripe ID, and succeeds once they do."""
    email = "portal_user@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "password123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Expect failure since user has no stripe_customer_id yet
    fail_res = await client.post(
        f"{settings.API_V1_STR}/billing/portal",
        json={"return_url": "http://localhost:3000/settings"},
        headers=headers
    )
    assert fail_res.status_code == 422
    assert "subscribe first" in fail_res.json()["detail"]

    # 2. Inject Stripe Customer ID into the user
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalar_one()
    user.stripe_customer_id = "cus_mock_12345"
    db.add(user)
    await db.commit()

    # 3. Portal request should now succeed
    success_res = await client.post(
        f"{settings.API_V1_STR}/billing/portal",
        json={"return_url": "http://localhost:3000/settings"},
        headers=headers
    )
    assert success_res.status_code == 200
    data = success_res.json()
    assert "portal_url" in data
    assert "portal=success" in data["portal_url"]


@pytest.mark.asyncio
async def test_billing_webhook_upgrade_and_downgrade(client: AsyncClient, db: AsyncSession) -> None:
    """Verify webhook completes customer subscription upgrades and demotions."""
    email = "webhook_target@example.com"
    register_res = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "password123"}
    )
    user_id = register_res.json()["id"]

    # 1. Trigger simulated checkout.session.completed event
    mock_checkout_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": user_id,
                "customer": "cus_mock_webhook",
                "subscription": "sub_mock_webhook"
            }
        }
    }

    headers = {"stripe-signature": "mock_signature"}
    webhook_res = await client.post(
        f"{settings.API_V1_STR}/billing/webhook",
        json=mock_checkout_event,
        headers=headers
    )
    assert webhook_res.status_code == 200
    assert webhook_res.json()["status"] == "success"

    # Verify database state upgraded
    db.expire_all()
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalar_one()
    assert user.subscription_tier == "pro"
    assert user.stripe_customer_id == "cus_mock_webhook"
    assert user.stripe_subscription_id == "sub_mock_webhook"

    # 2. Trigger simulated customer.subscription.deleted event
    mock_delete_event = {
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "customer": "cus_mock_webhook"
            }
        }
    }

    webhook_res_2 = await client.post(
        f"{settings.API_V1_STR}/billing/webhook",
        json=mock_delete_event,
        headers=headers
    )
    assert webhook_res_2.status_code == 200

    # Verify database state demoted back to free
    db.expire_all()
    res2 = await db.execute(stmt)
    user2 = res2.scalar_one()
    assert user2.subscription_tier == "free"
    assert user2.stripe_subscription_id is None
