from datetime import datetime, timedelta
from jose import jwt
from src import config as _config


def create_confirmation_token(email: str):
    expires = datetime.now() + timedelta(minutes=int(_config.JWT_EXPIRE_MINUTES))
    to_encode = {"sub": email, "exp": expires}
    return jwt.encode(
        to_encode, _config.JWT_SECRET_KEY, algorithm=_config.JWT_ALGORITHM
    )
