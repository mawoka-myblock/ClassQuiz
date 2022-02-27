from classquiz.config import settings
import sqlalchemy
from classquiz.db import metadata

engine = sqlalchemy.create_engine(settings.db_url)

metadata.create_all(engine)
