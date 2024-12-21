from sqlalchemy.orm import Session

from . import schemas as _schemas

from .. import models as _global_models


def upload_payment(db: Session, payment_inf: _schemas.Payment):
    db_payment = _global_models.Payment(
        user_id=payment_inf.user_id,
        song_id=payment_inf.song_id,
        amount=payment_inf.amount,
        status=payment_inf.status,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment
