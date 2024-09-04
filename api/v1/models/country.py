from sqlalchemy import Column, String, Integer

from sqlalchemy.orm import relationship
from api.v1.models.association import mod_country_association, country_trivia_association, country_submission_association
from api.v1.models.base_model import BaseTableModel



class Country(BaseTableModel):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    preferred_moderators = relationship(
        "Moderator", secondary=mod_country_association, back_populates="country_preferences"
    )


    trivias = relationship(
        "Trivia", secondary=country_trivia_association, back_populates="countries"
    )

    submissions = relationship(
        "Submission", secondary=country_submission_association, back_populates="countries"
    )
