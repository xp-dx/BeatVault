import base64

from . import database as _global_database, models as _global_models


async def create_database():
    async with _global_database.engine.begin() as conn:
        await conn.run_sync(_global_models.Base.metadata.create_all)


def converting_file_to_base64(file):
    file_data = file.read()
    return base64.b64encode(file_data).decode("utf-8") if file_data else file_data
