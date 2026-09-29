# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

"""The Excel export's rows, without a database: it is the only export in the MVP."""

from frogquiz.db.models import QuizQuestion
from frogquiz.routers.eximport import excel_rows


def q(question: str, answers: list[tuple[str, bool]], type_: str | None = "ABCD") -> QuizQuestion:
    return QuizQuestion(
        question=question,
        time="20",
        type=type_,
        answers=[{"answer": a, "right": r} for a, r in answers],
    )


def test_check_questions_are_exported_with_every_correct_answer():
    _, rows = excel_rows([q("<p>Pick two</p>", [("a", True), ("b", False), ("c", True)], "CHECK")])
    assert len(rows) == 1
    assert rows[0][7] == "1,3"


def test_titles_are_plain_text_not_editor_html():
    _, rows = excel_rows([q("<p>What is <b>2 &amp; 2</b>?</p>", [("4", True), ("5", False)])])
    assert rows[0][1] == "What is 2 & 2?"


def test_four_answers_keep_the_original_layout():
    header, rows = excel_rows([q("Q", [("a", True), ("b", False), ("c", False), ("d", False)])])
    assert header == [
        "Question",
        "1st Answer",
        "2nd Answer",
        "3rd Answer",
        "4th Answer",
        "Time Limit (max. 120)",
        "Correct Answers",
    ]
    assert rows[0] == [1, "Q", "a", "b", "c", "d", "20", "1"]


def test_a_fifth_answer_widens_the_sheet_instead_of_overwriting_the_time():
    answers = [(str(n), n == 5) for n in range(1, 7)]
    header, rows = excel_rows([q("Q", answers)])
    assert header[5:7] == ["5th Answer", "6th Answer"]
    assert rows[0][2:8] == ["1", "2", "3", "4", "5", "6"]
    assert rows[0][8] == "20"
    assert rows[0][9] == "5"


def test_a_question_with_no_type_is_an_old_abcd_question():
    _, rows = excel_rows([q("Q", [("a", True), ("b", False)], None)])
    assert len(rows) == 1
