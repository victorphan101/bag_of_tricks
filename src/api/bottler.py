from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    with db.engine.begin() as connection:
        for potions in potions_delivered:
            sql_select_string = connection.execute(sqlalchemy.text("SELECT num_red_portions from global_inventory"))
            quantity = sql_select_string.get("num_red_potions")
            
            #check if there are enough potions to be delivered
            if quantity >= potions.quantity:
                quantity = quantity - potions.quantity
            sql_text = ("UPDATE global_inventory SET num_red_potions = %f",quantity)
            result = connection.execute(sqlalchemy.text(sql_text))
    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions AS quantity from global_inventory"))

    return result

    '''
    check inventory for quantity
    index for each color: 0=red, 1=blue, 2=green
    get_quantity = potion_type[0]/100 * quantity
    
    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": 5,
            }
        ]'''
