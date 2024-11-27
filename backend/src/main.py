from fastapi import FastAPI

from .auth import router as auth_router
from .routers import users

from . import services as _services

app = FastAPI(
    title="BeatVault",
    description="It is a service for buying and selling music",
    version="0.0.1",
)

_services.create_database()

app.include_router(users.router)
app.include_router(auth_router.router)
