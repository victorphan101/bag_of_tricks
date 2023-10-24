from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    with db.engine.begin() as connection:
        return connection.execute(sqlalchemy.text("SELECT sku, name, quantity, price, potion_type from catalog LIMIT 20"))
    """return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": result.num_red_potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
"""