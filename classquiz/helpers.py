from classquiz.db.models import Quiz, User


async def get_meili_data(quiz: Quiz) -> dict:
    return {
        "id": str(quiz.id),
        "title": quiz.title,
        "description": quiz.description,
        "user": (await User.objects.filter(id=quiz.user_id).first()).username,
        "created_at": int(quiz.created_at.timestamp()),
    }
