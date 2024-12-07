from fastapi import APIRouter, HTTPException, responses, Request

import stripe

import json

from . import config as _config

router = APIRouter(tags=["payment"])

stripe.api_key = _config.STRIPE_SECRET_KEY


@router.get("/checkout/")
async def create_checkout_session(price: int = 10):
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "rub",
                    "product_data": {
                        "name": "FastAPI Stripe Checkout",
                    },
                    "unit_amount": price * 100,
                },
                "quantity": 1,
            }
        ],
        metadata={"user_id": 3, "email": "abc@gmail.com", "request_id": 1234567890},
        mode="payment",
        success_url=_config.BASE_URL + "/success/",
        cancel_url=_config.BASE_URL + "/cancel/",
        customer_email="ping@fastapitutorial.com",
    )
    return responses.RedirectResponse(checkout_session.url, status_code=303)


@router.post("/webhook/")
async def stripe_webhook(request: Request):
    payload = await request.body()
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        print("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    print("event received is", event)
    if event["type"] == "checkout.session.completed":
        payment = event["data"]["object"]
        amount = payment["amount_total"]
        currency = payment["currency"]
        user_id = payment["metadata"]["user_id"]  # get custom user id from metadata
        user_email = payment["customer_details"]["email"]
        user_name = payment["customer_details"]["name"]
        order_id = payment["id"]
        # save to db
        # send email in background task
    return {}
