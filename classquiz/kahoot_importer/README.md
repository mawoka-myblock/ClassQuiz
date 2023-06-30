<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

# Kahoot-Importer

With this package you can search kahoot-quizzes and get their data.

This library is also tested.

## Get

```python
from classquiz.kahoot_importer.get import get, _Response
from asyncio import run
# _Response ia a pydantic-object, so you have access to
# .dict() or .json(exclude={"kahoot"})

async def main():
    kahoot_quiz: _Response = await get("GAME_ID")
    print(kahoot_quiz.json(exclude={"kahoot"}))
run(main())
```


## Search

```python
from classquiz.kahoot_importer.search import search, _Response
from asyncio import run
# _Response ia a pydantic-object, so you have access to
# .dict() or .json(exclude={"kahoot"})

async def main():
    kahoot_quizzes: _Response = await search("QUERY")
    print(kahoot_quizzes.json())
run(main())
```


## Import-Quiz
This script is meant just to be used with classquiz, not alone.
---
*Kahoot! and the K! logo are trademarks of Kahoot! AS*
