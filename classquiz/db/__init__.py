import databases
import sqlalchemy

from classquiz.config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()
