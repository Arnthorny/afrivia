from sqlalchemy import Column, String, Integer

from sqlalchemy.orm import relationship
from api.v1.models.association import category_trivia_association, category_submission_association
from api.v1.models.base_model import BaseTableModel



class Category(BaseTableModel):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    category_trivias = relationship(
        "Trivia", secondary=category_trivia_association, back_populates="categories"
    )

    submissions = relationship(
        "Submission", secondary=category_submission_association, back_populates="categories"
    )