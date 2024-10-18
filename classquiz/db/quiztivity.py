# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from pydantic import BaseModel
import enum


class Pdf(BaseModel):
    url: str


class _MemoryCard(BaseModel):
    image: str | None = None
    text: str | None = None
    id: str


class Memory(BaseModel):
    cards: list[list[_MemoryCard]]


class Markdown(BaseModel):
    # skipcq: PTC-W0052
    markdown: str


class _AbcdAnswer(BaseModel):
    answer: str
    correct: bool


class Abcd(BaseModel):
    question: str
    answers: list[_AbcdAnswer]


class QuizTivityTypes(str, enum.Enum):
    SLIDE = "SLIDE"
    PDF = "PDF"
    MEMORY = "MEMORY"
    MARKDOWN = "MARKDOWN"
    ABCD = "ABCD"


TYPE_CLASS_LIST = {
    QuizTivityTypes.PDF: type(Pdf),
    QuizTivityTypes.MEMORY: type(Memory),
    QuizTivityTypes.MARKDOWN: type(Markdown),
    QuizTivityTypes.ABCD: type(Abcd),
}


class QuizTivityPage(BaseModel):
    title: str | None = None
    type: QuizTivityTypes
    data: Pdf | Memory | Markdown | Abcd
