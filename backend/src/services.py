import base64

from . import database as _database, models as _models


def create_database():
    return _models.Base.metadata.create_all(_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def converting_file_to_base64(file):
    file_data = file.read()
    return base64.b64encode(file_data).decode("utf-8") if file_data else file_data
