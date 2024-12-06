from pydantic import BaseModel


class Album(BaseModel):
    # id: int
    title: str
    description: str | None = None
