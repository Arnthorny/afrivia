from api.core.base.services import Service
from api.v1.models.country import Country
from sqlalchemy import or_
from api.v1.schemas.african_countries_enum import AfricanCountriesEnum as ACE


class CountryService(Service):
    @staticmethod
    def fetch_countries(
        db, list_of_countries: list[ACE] | None
    ) -> list[Country] | None:
        """This function retrieves country models

        Args:
            list_of_countries (list | None): List of country names whose models are required. Or none if not required

        Returns:
            list: List of Country models that match the given country names
        """
        if list_of_countries is None:
            return None
        if not list_of_countries:
            return []
        conditions = []

        for c_name in list_of_countries:
            conditions.append(Country.name == c_name.value)

        all_country_models = db.query(Country).filter(or_(*conditions)).all()

        return all_country_models
