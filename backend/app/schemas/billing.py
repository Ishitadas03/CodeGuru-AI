from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    """Schema requesting a Stripe Checkout Session generation."""
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    """Schema containing Stripe checkout session URL."""
    checkout_url: str


class PortalRequest(BaseModel):
    """Schema requesting a Stripe Customer Portal Session generation."""
    return_url: str


class PortalResponse(BaseModel):
    """Schema containing Stripe Customer Portal session URL."""
    portal_url: str
