from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum

import enum
from sqlalchemy.orm import relationship
from api.v1.models.association import (
    category_submission_association,
    country_submission_association,
)
from api.v1.models.base_model import BaseTableModel
from api.v1.schemas.submission import DifficultyEnum
from api.v1.schemas.submission import SubmissionStatusEnum


class Submission(BaseTableModel):
    __tablename__ = "submissions"

    question = Column(Text, unique=True, nullable=False)
    status = Column(
        Enum(SubmissionStatusEnum), nullable=False, default=SubmissionStatusEnum.pending
    )
    moderator_id = Column(String, ForeignKey("moderators.id"), nullable=True)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    submission_note = Column(Text)

    moderator = relationship("Moderator", back_populates="assigned_submissions")
    options = relationship(
        "SubmissionOption",
        back_populates="submission_question",
        cascade="all, delete-orphan",
    )

    categories = relationship(
        "Category",
        secondary=category_submission_association,
        back_populates="submissions",
    )

    countries = relationship(
        "Country",
        secondary=country_submission_association,
        back_populates="submissions",
    )

    def to_dict(self) -> dict:
        """returns a dictionary representation of the submission"""
        obj_dict = self.__dict__.copy()
        obj_dict.pop("_sa_instance_state", None)
        obj_dict["id"] = self.id

        # For now it's a one-to-one mapping for question and categories
        obj_dict["category"] = self.categories[0].name
        obj_dict["countries"] = list(map(lambda x: x.name, self.countries))

        obj_dict["correct_option"] = ""
        obj_dict["incorrect_options"] = []
        all_option_objects: list[SubmissionOption] = self.options

        for option_obj in all_option_objects:
            if option_obj.is_correct is True:
                obj_dict["correct_option"] = option_obj.content
            else:
                obj_dict["incorrect_options"].append(option_obj.content)

        return obj_dict


class SubmissionOption(BaseTableModel):
    __tablename__ = "submission_options"

    submission_id = Column(
        String, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)

    submission_question = relationship(
        "Submission", back_populates="options", uselist=False, passive_deletes=True
    )
