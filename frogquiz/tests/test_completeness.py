# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

"""The draft rule: which saved quizzes /quiz/start refuses. No database needed.

It mirrors frontend/src/lib/editor/question_complete.ts; the cases are the same ones.
"""

from frogquiz.db.models import QuizQuestionType
from frogquiz.helpers.completeness import question_is_complete, unfinished_questions


def q(**over):
    return {
        "question": "<p>Which of these is an amphibian?</p>",
        "time": "20",
        "type": "ABCD",
        "answers": [{"answer": "Tree frog", "right": True}, {"answer": "Gecko", "right": False}],
        **over,
    }


def test_a_runnable_question_is_complete():
    assert question_is_complete(q())
    assert question_is_complete(q(type=QuizQuestionType.CHECK)), "an enum before it is stored"
    assert question_is_complete(q(type=None)), "old questions saved before type existed"


def test_an_emptied_rich_text_title_is_blank():
    assert not question_is_complete(q(question="<p></p>"))
    assert not question_is_complete(q(question="<p> &nbsp; </p>")), "a non-breaking space is blank too"


def test_answers_need_two_texts_and_a_right_one():
    assert not question_is_complete(q(answers=[{"answer": "Only", "right": True}]))
    assert not question_is_complete(q(answers=[{"answer": "A", "right": False}, {"answer": "B", "right": False}]))
    # The server stores a blank answer as None.
    assert not question_is_complete(q(answers=[{"answer": "A", "right": True}, {"answer": None, "right": False}]))
    assert not question_is_complete(q(answers=[{"answer": "A", "right": True}, {"answer": "  ", "right": False}]))


def test_cut_types_in_old_quizzes_are_not_judged():
    # A TEXT question has one answer and no `right`; judging it by the ABCD rule would
    # make every old quiz that has one impossible to start.
    assert question_is_complete(q(type="TEXT", answers=[{"answer": "frog", "case_sensitive": False}]))
    assert question_is_complete(q(type="VOTING", answers=[{"answer": "A"}, {"answer": "B"}]))
    assert question_is_complete(q(type="RANGE", answers={"min": 0, "max": 10, "min_correct": 1, "max_correct": 2}))
    assert not question_is_complete(q(type="VOTING", question="")), "every question needs a title"


def test_unfinished_questions_are_numbered_from_one():
    assert unfinished_questions([q(), q(question=""), q(), q(answers=[])]) == [2, 4]
    assert unfinished_questions([q()]) == []
