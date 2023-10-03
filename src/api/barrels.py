from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)
    with db.engine.begin() as connection:
        for barrels in barrels_delivered:
            sql_select_string = connection.execute(sqlalchemy.text("SELECT num_red_portions, num_red_ml, gold from global_inventory"))
            quantity = sql_select_string.get("num_red_potions")
            num_red_ml = sql_select_string.get("num_red_ml")
            gold = sql_select_string.get("gold")
            
            #check if there is at least 10 potions from global_inventory
            #if not, check if there is 100ml to brew new potion
            num_red_ml = num_red_ml + barrels.ml_per_barrel
            if quantity < 10:
                while num_red_ml > 100:
                    quantity = quantity +1
                    num_red_ml = num_red_ml - 100
            #deliver the potion and claim the gold
            if quantity >= barrels.quantity:
                quantity = quantity - barrels.quantity
                gold = gold + barrels.price
            sql_text = ("UPDATE global_inventory SET num_red_potions = %f, num_red_ml = %f, gold = %f", quantity, num_red_ml, gold)
            result = connection.execute(sqlalchemy.text(sql_text))
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    #with db.engine.begin() as connection:
     #   result = connection.execute(sqlalchemy.text("SELECT * from global_inventory"))

    result = []
    for barrel in wholesale_catalog:
        new_dict ={}
        new_dict.update({"sku": barrel.sku})
        new_dict.update({"quantity": barrel.quantity})
        result.add(new_dict)
        
    return result
    '''
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]'''
