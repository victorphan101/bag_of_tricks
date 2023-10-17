from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

#Number of Carts
cart_id = 0

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    cart_id = cart_id + 1
    with db.engine.begin() as connection:
        sql_select_string = connection.execute(sqlalchemy.text("INSERT INTO customer_cart (cart_id, customer, quantity, payment, price) VALUES( :cart_id, :new_cart.customer, 0, 0, 0)"))
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    with db.engine.begin() as connection:
        return connection.execute(sqlalchemy.text("SELECT cart_id from customer_cart"))


class CartItem(BaseModel):
    quantity : int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        sql_select_string = connection.execute(sqlalchemy.text("UPDATE customer_cart SET quantity = :cart_item.quantity WHERE cart_id = :cart_id"))
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE customer_cart SET price = :cart_checkout.payment WHERE cart_id = :cart_id"))
        get_quantity = connection.execute(sqlalchemy.text("SELECT quantity from customer_cart WHERE cart_id = :cart_id"))
        return {"total_potions_bought" :get_quantity.get("quantity"), "total_gold_paid": cart_checkout.payment}
    """#total_potions-bought takes cart_id
    #total_gold_paid updates the global_inventory
    red_potions_bought = (cart_list_items.get(cart_id)).get("red_quantity")
    blue_potions_bought = (cart_list_items.get(cart_id)).get("blue_quantity")
    green_potions_bought = (cart_list_items.get(cart_id)).get("green_quantity")
    checkout_string = {"red_potions_bought": red_potions_bought, "blue_potions_bought": blue_potions_bought, "green_potions_bought": green_potions_bought, "total_gold_paid": cart_checkout.payment}
   
   
    with db.engine.begin() as connection:
        sql_select_string = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_blue_potions, num_green,potions, gold from global_inventory"))
        red_quantity = sql_select_string.get("num_red_potions") - red_potions_bought
        blue_quantity = sql_select_string.get("num_blue_potions") - blue_potions_bought
        green_quantity = sql_select_string.get("num_green_potions") - green_potions_bought
        num_gold = sql_select_string.get("gold") + cart_checkout.payment
        sql_text = ("UPDATE global_inventory SET num_red_potions = %f, num_blue_potions = %f, num_green_potions = %f, gold= %f", red_quantity, blue_quantity, green_quantity, num_gold)
        result = connection.execute(sqlalchemy.text(sql_text))
    del cart_list[cart_id]
    cart_list_items[cart_id] = []
    
    return checkout_string
"""