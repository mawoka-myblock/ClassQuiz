# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from ormar import DatabaseConnection
import sqlalchemy

from classquiz.config import settings

settings = settings()

database = DatabaseConnection(settings.db_url)
metadata = sqlalchemy.MetaData()
