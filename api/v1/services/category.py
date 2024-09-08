from api.core.base.services import Service
from api.v1.models.category import Category
from sqlalchemy import or_
from api.v1.schemas.submission import CategoryEnum as CE



class CategoryService(Service):
    @staticmethod
    def fetch_categories(db, list_of_categories: list[CE]) -> list[Category]:
        """This function retrieves category models 

        Args:
            list_of_categories (list): List of category names whose models are required

        Returns:
            list: List of Category models that match the given category names
        """
        if not list_of_categories:
            return []
        conditions = []

        for c_name in list_of_categories:
            conditions.append(Category.name == c_name.value)

        all_category_models = db.query(Category).filter(or_(*conditions)).all()

        return all_category_models