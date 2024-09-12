from sqlalchemy import Column, String, Boolean, Enum

from sqlalchemy.orm import relationship
from api.v1.models.association import mod_country_association
from api.v1.models.base_model import BaseTableModel


class Moderator(BaseTableModel):
    __tablename__ = "moderators"

    avatar_url = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    country_preferences = relationship(
        "Country",
        secondary=mod_country_association,
        back_populates="preferred_moderators",
    )

    assigned_submissions = relationship("Submission", back_populates="moderator")

    def to_dict(self) -> dict:
        """returns a dictionary representation of the submission"""
        obj_dict = self.__dict__.copy()
        obj_dict.pop("_sa_instance_state", None)
        obj_dict["id"] = self.id

        obj_dict["country_preferences"] = list(
            map(lambda x: x.name, self.country_preferences)
        )

        return obj_dict
