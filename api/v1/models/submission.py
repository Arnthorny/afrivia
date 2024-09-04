from sqlalchemy import (
    Column,
    String, Text, Boolean,
    ForeignKey, Enum)

import enum
from sqlalchemy.orm import relationship
from api.v1.models.association import category_submission_association, country_submission_association
from api.v1.models.base_model import BaseTableModel



class SubmissionStatusEnum(str, enum.Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'

class DifficultyEnum(str, enum.Enum):
    easy = 'easy'
    medium = 'medium'
    hard = 'hard'



class Submission(BaseTableModel):
    __tablename__ = 'submissions'

    question = Column(Text, unique=True, nullable=False)
    status = Column(Enum(SubmissionStatusEnum), nullable=False, default=SubmissionStatusEnum.pending)
    moderator_id = Column(String, ForeignKey('moderators.id'), nullable=False)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    submission_note = Column(Text)

    moderator = relationship("Moderator", back_populates="assigned_submissions")
    options = relationship("SubmissionOption", back_populates="submission_question")

    categories = relationship(
        "Category", secondary=category_submission_association, back_populates="submissions"
    )

    countries = relationship(
        "Country", secondary=country_submission_association, back_populates="submissions"
    )

class SubmissionOption(BaseTableModel):
    __tablename__ = 'submission_options'

    submission_id = Column(String, ForeignKey('submissions.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)

    submission_question = relationship("Submission", back_populates="options", uselist=False)