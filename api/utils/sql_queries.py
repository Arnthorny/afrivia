from sqlalchemy.orm import aliased
from sqlalchemy import desc, func, select, Select, asc
from api.v1.models.moderator import Moderator, mod_country_association
from api.v1.models.submission import Submission
from api.v1.models.country import Country


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
            func.coalesce(
                func.string_to_array(func.string_agg(subquery_1.c.c_name, ","), ","),
                "{}",
            ).label("country_preferences"),
            func.count(func.distinct(subquery_2.c.id)).label(
                "pending_submissions_count"
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
