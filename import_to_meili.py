import meilisearch
from classquiz.db.models import Quiz, User
from pprint import pprint
from classquiz.config import settings
from asyncio import run

settings = settings()


async def __main__():
    meili_data = []
    questions = await Quiz.objects.filter(public=True).all()
    for question in questions:
        meili_data.append({
            "id": str(question.id),
            "title": question.title,
            "description": question.description,
            "user": (await User.objects.filter(id=question.user_id).first()).username,
        })
    print(meili_data)
    client = meilisearch.Client(settings.meilisearch_url)
    client.index(settings.meilisearch_index).add_documents(meili_data)


if __name__ == "__main__":
    run(__main__())
