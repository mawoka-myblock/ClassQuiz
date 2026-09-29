# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

"""Whether a saved quiz can be played, or is still a draft (MVP.md D14).

The editor saves unfinished quizzes as they are typed, so "saved" no longer means
"playable". There is no draft column: a quiz is a draft exactly when one of its questions
is unfinished, worked out from the questions each time. A stored flag could disagree with
the questions it describes; this cannot.

The rule is the editor's own, `frontend/src/lib/editor/question_complete.ts`, and the two
must stay the same -- the editor marks questions with one and the server refuses to start
a game with the other.
"""

import html
from typing import Any

import bleach

# The two types the MVP offers (D2), plus old questions saved before `type` existed. The
# cut types have their own rules, enforced by their own editors when they were live, and
# old quizzes that use them have to stay playable, so they are not judged here.
_CHECKED_TYPES = {None, "ABCD", "CHECK"}


def _visible_text(value: Any) -> str:
    # Question titles are rich-text HTML: an emptied editor hands back "<p></p>".
    if not isinstance(value, str):
        return ""
    return html.unescape(bleach.clean(value, tags=[], strip=True)).strip()


def question_is_complete(question: dict[str, Any]) -> bool:
    if not _visible_text(question.get("question")):
        return False
    # A string from the database, or a QuizQuestionType before it has been stored.
    type_ = getattr(question.get("type"), "value", question.get("type"))
    if type_ not in _CHECKED_TYPES:
        return True
    answers = question.get("answers")
    if not isinstance(answers, list):
        # Only RANGE and SLIDE store answers that way; the editor's rule lets them through.
        return True
    if len(answers) < 2:
        return False
    if not all(isinstance(a, dict) and _visible_text(a.get("answer")) for a in answers):
        return False
    return any(a.get("right") for a in answers)


def unfinished_questions(questions: list[dict[str, Any]]) -> list[int]:
    """1-based numbers of the questions that stop this quiz from being played."""
    return [n for n, q in enumerate(questions, start=1) if not question_is_complete(q)]
