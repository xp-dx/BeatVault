from fastapi import FastAPI

from .auth import router as auth_router
from .songs import router as songs_router
from .albums import router as albums_router
from .payments import router as payment_router
from .users import router as users_router

from . import services as _services


app = FastAPI(
    title="BeatVault",
    description="It is a service for buying and selling music",
    version="0.0.1",
)

_services.create_database()

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(songs_router.router)
app.include_router(albums_router.router)
app.include_router(payment_router.router)
