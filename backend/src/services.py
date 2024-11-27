from . import database as _database, models as _models


def create_database():
    return _models.Base.metadata.create_all(_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
