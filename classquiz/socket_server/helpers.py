# SPDX-FileCopyrightText: 2025 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0
import aiohttp
from classquiz.config import settings
from classquiz.db.models import (
    PlayGame,
    QuizQuestionType,
    TextQuizAnswer,
    ABCDQuizAnswer,
    VotingQuizAnswer,
    RangeQuizAnswer,
    AnswerDataList,
)
from classquiz.socket_server.models import SubmitAnswerData
from .models import SubmitAnswerDataOrderType


async def check_captcha(captcha_data: str) -> bool:
    async with aiohttp.ClientSession() as session:
        try:
            if settings.hcaptcha_key is not None:
                try:
                    async with session.post(
                        "https://hcaptcha.com/siteverify",
                        data={
                            "response": captcha_data,
                            "secret": settings.hcaptcha_key,
                        },
                    ) as resp:
                        resp_data = await resp.model_dump_json()
                        if not resp_data["success"]:
                            return
                except KeyError:
                    return False
            elif settings.recaptcha_key is not None:
                async with session.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={
                        "secret": settings.recaptcha_key,
                        "response": captcha_data,
                    },
                ) as resp:
                    try:
                        resp_data = await resp.model_dump_json()
                        if not resp_data["success"]:
                            return False
                    except KeyError:
                        return False
        except TypeError:
            pass
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
    correct_string = ""
    for i, a in enumerate(answers):
        if a.right:
            correct_string += str(i)
    return bool(correct_string == answer)


async def has_already_answered(game_pin: str, q_index: int, username: str) -> bool:
    answers = await AnswerDataList.get_redis_or_empty(game_pin, q_index)
    if answers is None:
        return False
    else:
        answers = list(filter(lambda a: a.username == username, answers.root))
        return len(answers) > 0
