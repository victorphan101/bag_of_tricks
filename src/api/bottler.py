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
    with db.engine.begin() as connection:
        print(potions_delivered)

        for potions in potions_delivered:
            
            add_potions = sum(potions.quantity for potion in potions_delivered)
            red_ml = sum(potions.quantity * potions.potion_type[0] for potions in potions_delivered)
            green_ml = sum(potions.quantity * potions.potion_type[1] for potions in potions_delivered)
            blue_ml = sum(potions.quantity * potions.potion_type[2] for potions in potions_delivered)
            dark_ml = sum(potions.quantity * potions.potion_type[3] for potions in potions_delivered)
            
            for potion_delivered in potions_delivered:
                connection.execute(
                    sqlalchemy.text("UPDATE potions SET inventory = inventory + :add_potions WHERE type= :potion_type"), [{"add_potions" : potion_delivered.quantity, "potion_type": potion_delivered.potion_type}]
                )
                
            connection.execute(
                sqlalchemy.text("UPDATE globals SET red_ml = red_ml - :red_ml, green_ml = green_ml - :green_ml, blue_ml = blue_ml - :blue_ml, dark_ml = dark_ml - :dark_ml"), [{"red_ml" : red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml}]
            )
            
            #check if there are enough potions to be delivered
            """if red_count >= red_bottler:
                rec_count = red_count-red_bottler
            if blue_count >= blue_bottler:
                blue_count = blue_count-blue_bottler
            if green_count >= green_bottler:
                green_count = green_count-green_bottler
            sql_text = ("UPDATE global_inventory SET num_red_potions = %f, num_blue_potions = %f, num_green_potions = %f", red_count, blue_count, green_count)
            result = connection.execute(sqlalchemy.text(sql_text))"""
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

    with db.engine.begin() as connection:
        
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_blue_potions, num_green_potions from global_inventory"))

    return result

    '''
    check inventory for quantity
    index for each color: 0=red, 1=green, 2=blue
    get_quantity = potion_type[0]/100 * quantity
    
    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": 5,
            }
        ]'''
