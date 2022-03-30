import databases
import sqlalchemy

from classquiz.config import settings

settings = settings()

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()
