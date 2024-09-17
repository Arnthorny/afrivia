import enum

from sqlalchemy import Column, String, Boolean, Enum, Text, ForeignKey

from sqlalchemy.orm import relationship
from api.v1.models.association import (
    country_trivia_association,
    category_trivia_association,
)
from api.v1.models.base_model import BaseTableModel
from api.v1.schemas.submission import DifficultyEnum


class Trivia(BaseTableModel):
    __tablename__ = "trivias"

    question = Column(Text, nullable=False, unique=True)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    submission_id = Column(String, ForeignKey("submissions.id"))

    submission = relationship("Submission")
    options = relationship(
        "TriviaOption", back_populates="trivia_question", cascade="all, delete-orphan"
    )

    categories = relationship(
        "Category",
        secondary=category_trivia_association,
        back_populates="category_trivias",
    )

    countries = relationship(
        "Country", secondary=country_trivia_association, back_populates="trivias"
    )

    def to_dict(self) -> dict:
        """returns a dictionary representation of the trivia"""
        obj_dict = self.__dict__.copy()
        obj_dict.pop("_sa_instance_state", None)
        obj_dict["id"] = self.id

        # For now it's a one-to-one mapping for question and categories
        obj_dict["category"] = self.categories[0].name
        obj_dict["countries"] = list(map(lambda x: x.name, self.countries))

        obj_dict["correct_option"] = ""
        obj_dict["incorrect_options"] = []
        all_option_objects: list[TriviaOption] = self.options

        for option_obj in all_option_objects:
            if option_obj.is_correct is True:
                obj_dict["correct_option"] = option_obj.content
            else:
                obj_dict["incorrect_options"].append(option_obj.content)

        return obj_dict


class TriviaOption(BaseTableModel):
    __tablename__ = "trivia_options"

    trivia_id = Column(
        String, ForeignKey("trivias.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)

    trivia_question = relationship(
        "Trivia", back_populates="options", uselist=False, passive_deletes="all"
    )
