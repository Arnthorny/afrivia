from typing import Any, Dict, List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from api.db.database import Base

from api.utils.success_response import success_response


def paginated_response(
    db: Session,
    model,
    skip: int,
    limit: int,
    filters: Optional[Dict[str, Any]] = None,
) -> dict[str]:
    """
    Custom response for pagination.\n
    This takes in four arguments:
        * db- this is the database session
        * model- this is the database table model eg Product, Organisation```
        * limit- this is the number of items to fetch per page, this would be a query parameter
        * skip- this is the number of items to skip before fetching the next page of data. This would also
        be a query parameter
        * filters- this is an optional dictionary of filters to apply to the query

    Example use:
        **Without filter**
        ``` python
        return paginated_response(
            db=db,
            model=Product,
            limit=limit,
            skip=skip
        )
        ```

        **With filter**
        ``` python
        return paginated_response(
            db=db,
            model=Product,
            limit=limit,
            skip=skip,
            filters={'org_id': org_id}
        )
        ```
    """

    query = db.query(model)

    if filters:
        # Apply filters
        for attr, value in filters.items():
            if value is not None:
                column = getattr(model, attr)
                if isinstance(column.type, str):
                    # Handle string fields
                    query = query.filter(column.like(f"%{value}%"))
                else:
                    # Handle other types (e.g., Integer, DateTime, Boolean)
                    query = query.filter(column == value)

    total = query.count()
    results = query.order_by(model.created_at.desc()).offset(skip).limit(limit).all()

    # items = jsonable_encoder(results)
    try:
        total_pages = int(total / limit) + (total % limit > 0)
    except:
        total_pages = int(total / limit)

    paginated_data = {
        "total_pages": total_pages,
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": results,
    }
    return paginated_data
