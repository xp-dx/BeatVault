from pydantic import BaseModel

from decimal import Decimal


class Payment(BaseModel):
    user_id: int
    song_id: int
    amount: Decimal
    status: str
