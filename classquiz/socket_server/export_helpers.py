# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import json
from datetime import datetime

from pydantic import ValidationError

from classquiz.config import redis
from classquiz.db.models import PlayGame, GameResults


async def save_quiz_to_storage(game_pin: str):
    game = PlayGame.parse_raw(await redis.get(f"game:{game_pin}"))
    player_count = await redis.scard(f"game_session:{game_pin}:players")
    answers = []
    for i in range(len(game.questions)):
        redis_res = await redis.get(f"game_session:{game_pin}:{i}")
        try:
            answers.append(json.loads(redis_res))
        except (ValidationError, TypeError):
            answers.append([])
    player_scores = await redis.hgetall(f"game_session:{game_pin}:player_scores")
    custom_field_data = await redis.hgetall(f"game:{game_pin}:players:custom_fields")
    q_return = []
    for q in game.questions:
        q_return.append(q.dict())
    data = GameResults(
        id=game.game_id,
        quiz=game.quiz_id,
        user=game.user_id,
        timestamp=datetime.now(),
        player_count=player_count,
        answers=json.dumps(answers),
        player_scores=json.dumps(player_scores),
        custom_field_data=json.dumps(custom_field_data),
        title=game.title,
        description=game.description,
        questions=json.dumps(q_return),
    )
    await data.save()
