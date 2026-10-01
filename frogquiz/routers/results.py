# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from frogquiz.auth import get_current_user
from frogquiz.db.models import User, GameResults

router = APIRouter()


@router.get("/list")
async def list_game_results(
    user: User = Depends(get_current_user),
) -> list[GameResults]:
    results = (
        await GameResults.objects.select_related(GameResults.quiz)
        .order_by(GameResults.timestamp.desc())
        .all(user=user.id)
    )
    return results


@router.get("/list/{quiz_id}")
async def get_results_by_quiz(quiz_id: UUID, user: User = Depends(get_current_user)) -> list[GameResults]:
    res = await GameResults.objects.all(user=user.id, quiz=quiz_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")
    else:
        return res


@router.get("/{game_id}")
async def get_game_result(game_id: UUID, user: User = Depends(get_current_user)) -> GameResults:
    res = await GameResults.objects.select_related(GameResults.quiz).get_or_none(user=user.id, id=game_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")
    else:
        return res


class _SetNoteInput(BaseModel):
    note: str


@router.post("/set_note")
async def set_note(id: UUID, data: _SetNoteInput, user: User = Depends(get_current_user)) -> GameResults:
    res = await GameResults.objects.get_or_none(user=user.id, id=id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")
    res.note = data.note
    return await res.update()


# Upstream left a results-export route here as a bare string literal in the module body:
# it reads like a docstring, every linter flags it, and it looks as though uncommenting it
# would bring the feature back. It would not. The body referenced three names that do not
# exist anywhere in this module (`data`, `player_fields`, `score_data`) and called
# `datetime.strftime` on the class rather than an instance, so it has never been able to
# run. Kept as a comment instead, because it records the intended shape:
#
#   GET /results/export/{result_id} -> StreamingResponse
#     - GameResults.objects.get_or_none(user=user.id, id=result_id), 404 if missing
#     - build a Quiz from res.title and res.questions
#     - generate_spreadsheet(quiz=..., quiz_results=..., player_fields=..., player_scores=...)
#     - stream it as application/vnd.ms-excel, Content-Disposition attachment
#
# The live host-side export is the one that works, and it is not in this file: the host
# emits `get_export_token` over the socket (socket_server/__init__.py) and redeems it at
# GET /api/v1/quiz/export_data/{export_token}. /results itself is hidden for the MVP
# (MVP.md D4), so this is not a gap anyone can reach today.
