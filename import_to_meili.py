import meilisearch
from classquiz.db import database
from classquiz.db.models import Quiz
from classquiz.helpers import get_meili_data
from classquiz.config import settings
from asyncio import run

settings = settings()


async def __main__():
    if not database.is_connected:
        await database.connect()
    meili_data = []
    quizzes = await Quiz.objects.filter(public=True).all()
    for quiz in quizzes:
        meili_data.append(await get_meili_data(quiz))
    print(meili_data)
    client = meilisearch.Client(settings.meilisearch_url)
    client.index(settings.meilisearch_index).add_documents(meili_data)
    client.index(settings.meilisearch_index).update_settings({"sortableAttributes": ["created_at"]})


if __name__ == "__main__":
    run(__main__())
