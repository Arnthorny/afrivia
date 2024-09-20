from sqlalchemy.orm import aliased
from sqlalchemy import func, select, Select, asc, or_, ColumnElement, false, true, any_
from api.v1.models.moderator import Moderator, mod_country_association
from api.v1.models.submission import Submission
from api.v1.models.country import Country
from api.v1.models import (
    category_trivia_association,
    country_trivia_association,
    Category,
    Trivia,
)


def query_for_mods_pref_submissions() -> Select:
    """These sql select statements are used to build a query which results in a
    table containing 3 columns. One with the moderator's id, the second with an array
    of their country preferences and the last with a count of pending submissions assigned
    the mod

    Returns:
        Select: Sql alchemy select statement
    """

    # Aliases for tables
    mca = aliased(mod_country_association)
    sbm = aliased(Submission)

    # Subquery to connect moderators with their country preference if any
    subquery_1 = (
        select(mca.c.moderator_id.label("moderator_id"), Country.name.label("c_name"))
        .join(Country, mca.c.country_id == Country.id)
        .subquery()
    )

    # Subquery to connect moderators with their pending assigned submissions
    subquery_2 = (
        select(sbm.moderator_id.label("moderator_id"), sbm.id.label("id"))
        .where(sbm.status == "pending")
        .join(Moderator, sbm.moderator_id == Moderator.id)
        .subquery()
    )

    # Main query to join subquery tables and return required table
    query = (
        select(
            Moderator.id,
            func.array_remove(
                func.array_agg(func.distinct(subquery_1.c.name)), None
            ).label("country_preferences"),
            func.count(func.distinct(subquery_2.c.id)).label(
                "assigned_submissions_count"
            ),
        )
        .where(Moderator.is_active)
        .outerjoin(subquery_1, subquery_1.c.moderator_id == Moderator.id)
        .outerjoin(subquery_2, subquery_2.c.moderator_id == Moderator.id)
        .group_by(Moderator.id)
        .order_by(asc("pending_submissions_count"))
    )

    return query


def query_for_submission_stats() -> Select:
    """This query gets the number of total, pending, awaiting, approved and
       rejected submissions in the database

    Returns:
        Select: SQLAlchemy select statement
    """
    query = select(
        func.count().label("total"),
        func.count().filter(Submission.status == "pending").label("pending"),
        func.count().filter(Submission.status == "awaiting").label("awaiting"),
        func.count().filter(Submission.status == "approved").label("approved"),
        func.count().filter(Submission.status == "rejected").label("rejected"),
    )
    return query


def query_for_question_retrieval(
    filters: dict[str, ColumnElement | str | None] = {}, limit: int | None = None
) -> Select:
    """This statement queries the database for questions that match a given query.
    The query is passed as elements of the filters dict. The returned questions order is randomized

    Args:
        filters (dict[str, ColumnElement | str | None]): A dict containing as its values SQLAlchemy
        ColumnElements or a string which is in turn used in filter statements
        limit (int | None, optional): The number of trivias to return. Defaults to None.

    Returns:
        Select: Sqlalchemy select statement
    """
    catr_alias = aliased(category_trivia_association)
    cntriv_alias = aliased(country_trivia_association)

    countries_arr = func.array_remove(func.array_agg(Country.name), None)

    # filters['countries'] value is passed as a string | None to enable comparison with
    # the countries_arr label
    if (tmp := filters.pop("country", None)) is not None:
        filters["country"] = any_(countries_arr) == tmp

    # Build the query
    query = (
        select(Trivia)
        .join(catr_alias, catr_alias.c.trivia_id == Trivia.id, isouter=True)
        .join(Category, catr_alias.c.category_id == Category.id, isouter=True)
        .join(cntriv_alias, cntriv_alias.c.trivia_id == Trivia.id, isouter=True)
        .join(Country, cntriv_alias.c.country_id == Country.id, isouter=True)
        .filter(filters.pop("category", true()), filters.pop("difficulty", true()))
        .group_by(Trivia.id, Category.name)
        .having(or_(filters.pop("country", true()), countries_arr == []))
        .limit(limit)
        .order_by(func.random())
    )

    return query
