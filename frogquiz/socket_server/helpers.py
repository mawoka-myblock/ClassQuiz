# SPDX-FileCopyrightText: 2025 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0
import logging

import aiohttp
from redis.exceptions import WatchError

from frogquiz.config import settings, redis
from frogquiz.db.models import (
    PlayGame,
    QuizQuestionType,
    TextQuizAnswer,
    ABCDQuizAnswer,
    VotingQuizAnswer,
    RangeQuizAnswer,
    AnswerDataList,
    AnswerData,
)
from frogquiz.socket_server.models import SubmitAnswerData
from .models import SubmitAnswerDataOrderType

logger = logging.getLogger(__name__)


async def check_captcha(captcha_data: str) -> bool:
    """Verify a captcha response. False means "do not let this join through".

    With neither provider key set this fell through to `return True`, so a game with
    `captcha_enabled` and no configured secret admitted everyone while looking protected
    -- which is worse than no captcha, because the operator believes it is working.
    A control that cannot verify must not pass.

    `routers/quiz.py` refuses to store `captcha_enabled` without a configured key, so in
    practice this branch is unreachable; it is here so that removing a key later fails
    closed and says why, rather than silently reopening the door.
    """
    # `settings` is config.py's lru_cached *function*, imported uncalled. Every read in
    # here was `settings.hcaptcha_key` on the wrapper, which raises AttributeError -- and
    # AttributeError is not in the except clause below, so this did not "pass everyone":
    # it propagated out of join_game. Either way a captcha-enabled game was broken.
    config = settings()
    if config.hcaptcha_key is None and config.recaptcha_key is None:
        logger.warning("captcha check requested but no HCAPTCHA_KEY or RECAPTCHA_KEY is set; refusing the join")
        return False
    async with aiohttp.ClientSession() as session:
        try:
            if config.hcaptcha_key is not None:
                async with session.post(
                    "https://hcaptcha.com/siteverify",
                    data={
                        "response": captcha_data,
                        "secret": config.hcaptcha_key,
                    },
                ) as resp:
                    resp_data = await resp.json()
                    if not resp_data["success"]:
                        return False
            else:
                async with session.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={
                        "secret": config.recaptcha_key,
                        "response": captcha_data,
                    },
                ) as resp:
                    resp_data = await resp.json()
                    if not resp_data["success"]:
                        return False
        except (KeyError, TypeError, ValueError, aiohttp.ClientError):
            return False
    return True


def check_answer(game_data: PlayGame, data: SubmitAnswerData) -> (bool, str):
    q_i = int(float(data.question_index))
    q_type = game_data.questions[q_i].type
    q_answers = game_data.questions[q_i].answers
    q_answer = data.answer
    if q_type == QuizQuestionType.ABCD:
        return (check_abcd_question(q_answer, q_answers), data.answer)
    elif q_type == QuizQuestionType.RANGE:
        return (
            check_range_question(q_answer, q_answers),
            q_answer,
        )
    elif q_type == QuizQuestionType.VOTING:
        return (False, q_answer)
    elif q_type == QuizQuestionType.ORDER:
        return check_order_question(data.complex_answer, q_answer, q_answers)
    elif q_type == QuizQuestionType.TEXT:
        return (
            check_text_question(q_answer, q_answers),
            q_answer,
        )

    elif q_type == QuizQuestionType.CHECK:
        return (
            check_check_question(q_answer, q_answers),
            q_answer,
        )
    else:
        return (False, q_answer)
    return (False, q_answer)


def check_abcd_question(answer: str, answers: ABCDQuizAnswer) -> bool:
    for a in answers:
        if a.answer == answer and a.right:
            return True
    return False


def check_range_question(answer: str, answers: RangeQuizAnswer) -> bool:
    if answers.min_correct <= int(float(answer)) <= answers.max_correct:
        return answers.min_correct <= int(float(answer)) <= answers.max_correct


def check_order_question(
    complex_answer: list[SubmitAnswerDataOrderType] | None,
    answer: str,
    answers: list[VotingQuizAnswer],
) -> (bool, str):
    if complex_answer is None:
        return (False, answer)
    correct_answers = [{"answer": a.answer} for a in answers]
    submitted_answers = [{"answer": a.answer} for a in complex_answer]
    answer_str = ", ".join(a["answer"] for a in submitted_answers)
    is_correct = submitted_answers == correct_answers
    return is_correct, answer_str


def check_text_question(answer: str, answers: list[TextQuizAnswer]) -> bool:
    for q in answers:
        if q.case_sensitive:
            if answer == q.answer:
                return True
        else:
            if answer.lower() == q.answer.lower():
                return True
    return False


def check_check_question(answer: str, answers: list[ABCDQuizAnswer]) -> bool:
    """Score a multiple-answer question. All or nothing.

    The player submits the indices of every option they ticked, concatenated in
    ascending order, so ticking the first and third of four options sends "02". The
    same string is built here from the options marked right, and the two are compared
    whole: a partly correct set scores zero, and so does a correct set with one extra
    tick. There is no partial credit, deliberately -- a room cannot reason about a
    score it cannot predict, and half marks make "select all that apply" pay off for
    ticking everything.

    The format is only unambiguous while a question has fewer than ten options, which
    the editor enforces by capping a question at four answers.
    """
    correct_string = ""
    for i, a in enumerate(answers):
        if a.right:
            correct_string += str(i)
    return bool(correct_string == answer)


async def record_answer_once(game_pin: str, q_index: int, data: AnswerData) -> AnswerDataList | None:
    """Append one player's answer to a question, unless they already have one there.

    Returns the updated list, or None if this player had already answered.

    The list is one JSON value per question, read by eight places, so it is updated in
    a WATCH/MULTI transaction rather than changed to a Redis list. The old code read it,
    appended and wrote it back with nothing in between, so answers arriving together
    overwrote each other: 50 players answering at once kept one or two of them. The
    duplicate check has to be inside the same transaction, or two quick taps from one
    player both pass it.
    """
    key = f"game_session:{game_pin}:{q_index}"
    async with redis.pipeline(transaction=True) as pipe:
        while True:
            try:
                await pipe.watch(key)
                raw = await pipe.get(key)
                answers = AnswerDataList([]) if raw is None else AnswerDataList.model_validate_json(raw)
                if any(a.username == data.username for a in answers):
                    await pipe.unwatch()
                    return None
                answers.append(data)
                pipe.multi()
                pipe.set(key, answers.model_dump_json(), ex=7200)
                await pipe.execute()
                return answers
            except WatchError:
                # Somebody else's answer landed between our read and our write. Read
                # again; nothing of ours was written.
                continue


async def has_already_answered(game_pin: str, q_index: int, username: str) -> bool:
    answers = await AnswerDataList.get_redis_or_empty(game_pin, q_index)
    if answers is None:
        return False
    else:
        answers = list(filter(lambda a: a.username == username, answers.root))
        return len(answers) > 0
