from fastapi import APIRouter, HTTPException, responses, Request, Depends

from sqlalchemy.orm import Session

import stripe

import json

from typing import Annotated

from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas

from . import config as _config, crud as _crud, schemas as _schemas

from .. import dependencies as _global_dependencies, models as _global_models

router = APIRouter(tags=["payment"])

stripe.api_key = _config.STRIPE_SECRET_KEY
endpoint_secret = _config.ENDPOINT_SECRET


@router.get("/checkout/{song_id}")
async def create_checkout_session(
    current_user: Annotated[
        _auth_schemas.UserEmail, Depends(_auth_dependencies.get_current_active_user)
    ],
    song_id: int,
    db: Session = Depends(_global_dependencies.get_db),
    # current_user_id=1,
):
    # current_user = (
    #     db.query(_global_models.User)
    #     .filter(_global_models.User.id == current_user_id)
    #     .first()
    # )
    song = (
        db.query(_global_models.Song).filter(_global_models.Song.id == song_id).first()
    )

    seller_id = (
        db.query(_global_models.UserSong)
        .filter(_global_models.UserSong.song_id == song.id)
        .first()
        .user_id
    )
    seller = (
        db.query(_global_models.User)
        .filter(_global_models.User.id == seller_id)
        .first()
    )

    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "rub",
                    "product_data": {
                        "name": song.title,
                    },
                    "unit_amount": int(song.price * 100),
                },
                "quantity": 1,
            }
        ],
        metadata={
            "user_id": current_user.id,
            "song_id": song.id,
        },
        mode="payment",
        success_url=_config.BASE_URL + f"/download-song/{song_id}",
        cancel_url=_config.BASE_URL + "/songs",
        customer_email=current_user.email,
        payment_intent_data={
            "transfer_data": {
                "destination": seller.stripe_account_id,
            }
        },
    )
    return responses.RedirectResponse(checkout_session.url, status_code=303)


@router.post("/webhook/")
async def stripe_webhook(
    request: Request, db: Session = Depends(_global_dependencies.get_db)
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret
        )
    except ValueError as e:
        print("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    print("event received is", event)
    if event["type"] == "checkout.session.completed":
        payment = event["data"]["object"]
        amount = payment["amount_total"] / 100
        user_id = payment["metadata"]["user_id"]
        song_id = payment["metadata"]["song_id"]
        status = "successfully"

        payment_inf = _schemas.Payment(
            user_id=user_id, song_id=song_id, amount=amount, status=status
        )
        _crud.upload_payment(db=db, payment_inf=payment_inf)
        return {"status": "success"}
    return {"status": "event not handled"}
