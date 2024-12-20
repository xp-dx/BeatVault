from pydantic import BaseModel

from decimal import Decimal

from datetime import datetime


class Payment(BaseModel):
    # id: int
    user_id: int
    song_id: int
    amount: Decimal
    # payment_date: datetime
    status: str
