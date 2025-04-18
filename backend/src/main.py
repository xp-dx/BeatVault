from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.celery.redis_manager import redis_manager

from .auth import router as auth_router
from .songs import router as songs_router
from .albums import router as albums_router
from .payments import router as payment_router
from .users import router as users_router
from .admin import router as admin_router

from . import services as _global_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _global_services.create_database()
    await redis_manager.init()  # Инициализация один раз
    yield
    await redis_manager.close()


app = FastAPI(
    title="BeatVault",
    description="It is a service for buying and selling music",
    version="0.0.1",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(songs_router.router)
app.include_router(albums_router.router)
app.include_router(payment_router.router)
app.include_router(admin_router.router)
