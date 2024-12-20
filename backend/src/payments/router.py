from fastapi import APIRouter, HTTPException, responses, Request, Depends

from sqlalchemy.orm import Session

import stripe

import json

from typing import Annotated

from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas

from . import config as _config

from .. import dependencies as _global_dependencies, models as _global_models

router = APIRouter(tags=["payment"])

stripe.api_key = _config.STRIPE_SECRET_KEY


@router.get("/checkout/{song_id}")
async def create_checkout_session(
    # current_user: Annotated[
    #     _auth_schemas.UserEmail, Depends(_auth_dependencies.get_current_active_user)
    # ],
    song_id: int,
    db: Session = Depends(_global_dependencies.get_db),
    current_user_id=1,
):
    current_user = (
        db.query(_global_models.User)
        .filter(_global_models.User.id == current_user_id)
        .first()
    )
    song = (
        db.query(_global_models.Song).filter(_global_models.Song.id == song_id).first()
    )
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "rub",
                    "product_data": {
                        "name": song.title,
                    },
                    "unit_amount": song.price,
                },
                # "quantity": 1,
            }
        ],
        metadata={
            "user_id": current_user.id,
            "email": current_user.email,
            "song_id": song.id,
        },
        mode="payment",
        success_url=_config.BASE_URL + f"/download-song/{song_id}",
        cancel_url=_config.BASE_URL + "/songs",
        customer_email=current_user.email,
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
