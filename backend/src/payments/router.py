from fastapi import APIRouter, HTTPException, Request, Depends, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import stripe

from typing import Annotated

from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas
from src.songs import service as _songs_service
from src.auth import service as _auth_service


from . import config as _config, crud as _crud, schemas as _schemas

from .. import dependencies as _global_dependencies, models as _global_models

router = APIRouter(tags=["payment"], prefix="/payment")

stripe.api_key = _config.STRIPE_SECRET_KEY
endpoint_secret = _config.ENDPOINT_SECRET


@router.get("/checkout/{song_id}")
async def create_checkout_session(
    current_user: Annotated[
        _auth_schemas.UserEmail, Depends(_auth_dependencies.get_current_active_user)
    ],
    song_id: int,
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    song_result = await db.execute(
        select(_global_models.Song).where(_global_models.Song.id == song_id)
    )
    song = song_result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    user_song_result = await db.execute(
        select(_global_models.UserSong.user_id).where(
            _global_models.UserSong.song_id == song.id
        )
    )
    seller_id = user_song_result.scalar_one_or_none()
    if not seller_id:
        raise HTTPException(status_code=404, detail="Song owner not found")

    seller_result = await db.execute(
        select(_global_models.User).where(_global_models.User.id == seller_id)
    )
    seller = seller_result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    # Проверяем доступ
    user_result = await _auth_service.get_user_by_email(db=db, email=current_user.email)
    has_access = await _songs_service.check_access_to_song(user_result, song, db)
    if has_access:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have access to this song",
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
        success_url=_config.BASE_URL + f"/songs/download-song/{song_id}",
        cancel_url=_config.BASE_URL + "/songs",
        customer_email=current_user.email,
        # payment_intent_data={
        #     "transfer_data": {
        #         "destination": seller.stripe_account_id,
        #     }
        # },
    )
    return {"redirect_url": checkout_session.url}


@router.post("/webhook/")
async def stripe_webhook(
    request: Request, db: AsyncSession = Depends(_global_dependencies.get_async_session)
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret
        )
    except ValueError:
        print("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        print("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    print("event received is", event)

    if event["type"] == "checkout.session.completed":
        payment = event["data"]["object"]
        amount = payment["amount_total"] / 100
        user_id = int(payment["metadata"]["user_id"])
        song_id = int(payment["metadata"]["song_id"])
        status = "successfully"

        payment_inf = _schemas.Payment(
            user_id=user_id, song_id=song_id, amount=amount, status=status
        )

        await _crud.upload_payment(db=db, payment_inf=payment_inf)
        return {"status": "success"}

    return {"status": "event not handled"}
