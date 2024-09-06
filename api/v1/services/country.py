from api.core.base.services import Service
from api.v1.models.country import Country
from sqlalchemy import or_




class CountryService(Service):
    @staticmethod
    def fetch_countries(db, list_of_countries: list) -> list[Country]:
        """This function retrieves country models 

        Args:
            list_of_countries (list): List of country names whose models are required

        Returns:
            list: List of Country models that match the given country names
        """
        if not list_of_countries:
            return []
        conditions = []

        for c_name in list_of_countries:
            conditions.append(Country.name == c_name)

        all_country_models = db.query(Country).filter(or_(*conditions)).all()

        return all_country_models

        