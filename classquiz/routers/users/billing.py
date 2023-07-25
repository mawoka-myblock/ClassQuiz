# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0
import enum
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.config import stripe, settings, redis
from fastapi.responses import RedirectResponse
from classquiz.db.models import User, Subscription, SubscriptionPlans
from typing import Any

router = APIRouter()
settings = settings()


class BillingPlans(enum.Enum):
    ANNUAL = "ANNUAL"
    MONTHLY = "MONTHLY"


class BillingInput(BaseModel):
    plan: BillingPlans


class SubscribeToPlanResponse(BaseModel):
    subscription_id: str
    client_secret: str


@router.post("/subscribe", response_model=SubscribeToPlanResponse)
async def subscribe_to_plan(data: BillingInput, user: User = Depends(get_current_user)):
    stripe_id = user.stripe_id
    if stripe_id is None:
        stripe_user = stripe.Customer.create(email=user.email, name=user.username)
        stripe_id = stripe_user.id
    if data.plan == BillingPlans.ANNUAL:
        price_id = settings.stripe.annual_id
    elif data.plan == BillingPlans.MONTHLY:
        price_id = settings.stripe.monthly_id
    else:
        raise NotImplementedError("Enum has value which it mustn't have")
    try:
        subscription = stripe.Subscription.create(
            customer=stripe_id,
            items=[{"price": price_id}],
            cancel_at_period_end=False,
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
        )
        return SubscribeToPlanResponse(
            subscription_id=subscription.id, client_secret=subscription.latest_invoice.payment_intent.client_secret
        )
    except Exception as e:
        print(type(e))
        raise HTTPException(status_code=400, detail=e.user_message)


class StripeWebhookEvent(BaseModel):
    id: str
    api_version: str
    data: dict[str, Any]
    request: dict[str, Any]
    type: str


@router.post("/webhook")
async def receive_stripe_webhook(request: Request, request_data: StripeWebhookEvent):
    sig_header = request.headers.get("stripe-signature")
    data = request_data.data
    try:
        stripe.Webhook.construct_event(
            payload=await request.body(), sig_header=sig_header, secret=settings.stripe.webhook_secret
        )
    except Exception as e:
        return e
    if request_data.type == "invoice.paid":
        print(data)
    if request_data.type == "invoice.payment_failed":
        print(data)
    if request_data.type == "customer.subscription.deleted":
        user = await User.objects.get_or_none(stripe_id=data["object"]["customer"])
        if user is None:
            stripe_user = stripe.Customer.retrieve(data["object"]["customer"])
            user = await User.objects.get_or_none(email=stripe_user["email"])
            user.stripe_id = data["object"]["customer"]
        if data["object"]["status"] == "active":
            user.premium = True
        else:
            user.premium = False
        await user.update()
        await redis.delete(user.email)
    if request_data.type == "customer.subscription.updated":
        print("subscription updated")
        user = await User.objects.get_or_none(stripe_id=data["object"]["customer"])
        if user is None:
            stripe_user = stripe.Customer.retrieve(data["object"]["customer"])
            user = await User.objects.get_or_none(email=stripe_user["email"])
            user.stripe_id = data["object"]["customer"]
        if data["object"]["status"] == "active":
            user.premium = True
        else:
            user.premium = False
        await user.update()
        await redis.delete(user.email)
        price_id = data["object"]["items"]["data"][0]["plan"]["id"]
        if price_id == settings.stripe.annual_id:
            sub_type = SubscriptionPlans.ANNUAL
        elif price_id == settings.stripe.monthly_id:
            sub_type = SubscriptionPlans.MONTHLY
        Subscription(
            user=user.id,
            active=user.premium,
            subscription_id=data["object"]["id"],
            subscription_status=data["object"]["status"],
            product_id=price_id,
            type=sub_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    # else:
    #     print(json.dumps(request_data.data))
    #     print(request_data.type)
    print(request_data.type)
    return {"status": "success"}


@router.get("/portal-session")
async def generate_customer_portal_session(
    return_url: str = "/account/settings", user: User = Depends(get_current_user)
):
    if user.stripe_id is None:
        raise HTTPException(status_code=424, detail="No stripe id connected to your account")
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_id, return_url=f"{settings.root_address}{return_url}"
    )
    return RedirectResponse(session.url)
