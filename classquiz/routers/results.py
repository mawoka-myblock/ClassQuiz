# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.db.models import User, GameResults

router = APIRouter()


@router.get("/list")
async def list_game_results(user: User = Depends(get_current_user)) -> list[GameResults]:
    results = await GameResults.objects.select_related(GameResults.quiz).all(user=user.id)
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


# skipcq: PYL-W0105
"""
@router.get("/export/{result_id}", response_class=StreamingResponse)
async def export_result(result_id: UUID, user: User = Depends(get_current_user)):
    res = await GameResults.objects.get_or_none(user=user.id, id=result_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Game Result not found")
    quiz = Quiz(title=res.title, questions=res.questions)
    spreadsheet = await generate_spreadsheet(
        quiz=quiz, quiz_results=data, player_fields=player_fields, player_scores=score_data
    )

    def iter_file():
        yield from spreadsheet

    return StreamingResponse(
        iter_file(),
        media_type="application/vnd.ms-excel",
        headers={
            "Content-Disposition": f"attachment;filename=ClassQuiz-{urllib.parse.quote(quiz.title)}-{datetime.strftime('%m-%d-%Y')}.xlsx"
            # noqa: E501
        },
    )

"""
