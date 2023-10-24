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
            #quantity = red_count + green_count + blue_count
            quantity = 0
            red_count = 0
            green_count = 0
            blue_count = 0
            
            #ml_amount = red_ml + green_ml + blue_ml
            red_ml = 0
            green_ml = 0
            blue_ml = 0
            
            #condition for enough potions
            enough_red = True
            enough_blue = True
            enough_green = True
             
            gold_sql_select_string = connection.execute(sqlalchemy.text("SELECT gold from global_inventory"))
            gold = gold_sql_select_string.get("gold")

            
            if barrels.potion_type[0] > 0: 
                red_sql_select_string = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_red_ml from global_inventory"))
                red_count = red_sql_select_string.get("num_red_potions")
                red_in_barrel = ((barrels.potion_type[0])/10) * barrels.quantity
                
                red_ml = red_sql_select_string.get("num_red_ml")
            
                #check if there is at least 10 potions from global_inventory
                #if not, check if there is 100ml to brew new potion
                red_ml_barrel = (((barrels.potion_type[0])/10) *barrels.ml_per_barrel)
                if red_count < 10:
                    while red_ml > 100:
                        red_count = red_count +1
                        red_ml = red_ml - 100
                        
                if red_count >= red_in_barrel:
                    enough_red = True
                else:
                    enough_red = False
                        
            if barrels.potion_type[1] > 0: 
                blue_sql_select_string = connection.execute(sqlalchemy.text("SELECT num_blue_potions, num_blue_ml from global_inventory"))
                blue_count = blue_sql_select_string.get("num_blue_potions")
                blue_in_barrel = ((barrels.potion_type[1])/10) * barrels.quantity
                
                blue_ml = blue_sql_select_string.get("num_blue_ml")
            
                #check if there is at least 10 potions from global_inventory
                #if not, check if there is 100ml to brew new potion
                blue_ml_barrel = (((barrels.potion_type[1])/10) *barrels.ml_per_barrel)
                if blue_count < 10:
                    while blue_ml > 100:
                        blue_count = blue_count +1
                        blue_ml = blue_ml - 100
                        
                if blue_count >= blue_in_barrel:
                    enough_blue = True
                else:
                    enough_blue = False
                        
            if barrels.potion_type[2] > 0: 
                green_sql_select_string = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml from global_inventory"))
                green_count = green_sql_select_string.get("num_green_potions")
                green_in_barrel = ((barrels.potion_type[2])/10) * barrels.quantity
                
                green_ml = green_sql_select_string.get("num_green_ml")
            
                #check if there is at least 10 potions from global_inventory
                #if not, check if there is 100ml to brew new potion
                green_ml_barrel = (((barrels.potion_type[2])/10) *barrels.ml_per_barrel)
                if green_count < 10:
                    while green_ml > 100:
                        green_count = green_count +1
                        green_ml = green_ml - 100
                        
                if green_count >= green_in_barrel:
                    enough_blue = True
                else:
                    enough_blue = False
            
            #check if there is enough potions to finish the delivery
            #deliver the potion and claim the gold
            if enough_red and enough_blue and enough_green:
                quantity = quantity - barrels.quantity
                gold = gold + barrels.price     
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_count, num_red_ml = :red_ml, num_blue_potions = :blue_count, num_blue_ml = :blue_ml, num_green_potions = :green_count, num_green_ml = :green_ml, gold = :gold"))
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
        
        #count the quantities
        quantity = (((barrel.potion_type[0])/10) * barrel.quantity) + (((barrel.potion_type[1])/10) * barrel.quantity) + (((barrel.potion_type[2])/10) * barrel.quantity)
        new_dict.update({"quantity" : quantity})
        result.add(new_dict)
        
    return result
    '''
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]'''
