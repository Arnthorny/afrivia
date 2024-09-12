from sqlalchemy import Column, Integer, String, ForeignKey, Table

from api.db.database import Base


mod_country_association = Table(
    "mod_country_preferences",
    Base.metadata,
    Column(
        "moderator_id",
        String,
        ForeignKey("moderators.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("country_id", Integer, ForeignKey("countries.id"), primary_key=True),
)

category_submission_association = Table(
    "categories_submissions",
    Base.metadata,
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
    Column(
        "submission_id",
        String,
        ForeignKey("submissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

country_submission_association = Table(
    "countries_submissions",
    Base.metadata,
    Column("country_id", Integer, ForeignKey("countries.id"), primary_key=True),
    Column(
        "submission_id",
        String,
        ForeignKey("submissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

category_trivia_association = Table(
    "categories_trivias",
    Base.metadata,
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
    Column(
        "trivia_id",
        String,
        ForeignKey("trivias.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

country_trivia_association = Table(
    "countries_trivias",
    Base.metadata,
    Column("country_id", Integer, ForeignKey("countries.id"), primary_key=True),
    Column(
        "trivia_id",
        String,
        ForeignKey("trivias.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
