import enum

from sqlalchemy import Column, String, Boolean, Enum, Text, ForeignKey

from sqlalchemy.orm import relationship
from api.v1.models.association import (
    country_trivia_association,
    category_trivia_association,
)
from api.v1.models.base_model import BaseTableModel


class DifficultyEnum(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Trivia(BaseTableModel):
    __tablename__ = "trivias"

    question = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    submission_id = Column(String, ForeignKey("submissions.id"))

    submission = relationship("Submission")
    options = relationship("TriviaOption", back_populates="trivia_question")

    categories = relationship(
        "Category",
        secondary=category_trivia_association,
        back_populates="category_trivias",
    )

    countries = relationship(
        "Country", secondary=country_trivia_association, back_populates="trivias"
    )


class TriviaOption(BaseTableModel):
    __tablename__ = "trivia_options"

    trivia_id = Column(
        String, ForeignKey("trivias.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)

    trivia_question = relationship(
        "Trivia", back_populates="options", uselist=False, passive_deletes=True
    )
