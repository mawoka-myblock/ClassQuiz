#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from classquiz.config import settings
import sqlalchemy
from classquiz.db import metadata

engine = sqlalchemy.create_engine(settings().db_url)

metadata.create_all(engine)
print("Database setup finished!")
