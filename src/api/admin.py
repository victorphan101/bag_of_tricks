from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        return connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions=0, num_red_ml=0, gold=100"))



@router.get("/shop_info/")
def get_shop_info():
    """ """

    return {
        "shop_name": "Bag of Tricks",
        "shop_owner": "Victor Phan",
    }

