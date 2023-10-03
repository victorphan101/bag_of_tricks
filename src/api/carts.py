from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

#Number of Carts
cart_id = 0

#list of NewCart (cart_id as index)
cart_list = {}

#list of items in each cart (cart_id as index)
cart_list_items = []

#list of payments(a queue??)
payments_made = {}

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
    cart_list.add({cart_id : new_cart})
    cart_list_items.add([]) 
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    result = cart_list.get(cart_id)
    return result


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    cart_list_items.insert(cart_id, {"sku": item_sku, "quantity": cart_item.quantity})
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #total_potions-bought takes cart_id
    #total_gold_paid updates the global_inventory
    total_potions_bought = (cart_list_items.get(cart_id)).get("quantity")
    checkout_string = {"total_potions_bought": total_potions_bought, "total_gold_paid": cart_checkout.payment}
    with db.engine.begin() as connection:
        sql_select_string = connection.execute(sqlalchemy.text("SELECT num_red_portions, gold from global_inventory"))
        quantity = sql_select_string.get("num_red_portions") - total_potions_bought
        num_gold = sql_select_string.get("gold") + cart_checkout.payment
        sql_text = ("UPDATE global_inventory SET num_red_potions = %f, gold= %f",quantity, num_gold)
        result = connection.execute(sqlalchemy.text(sql_text))
    del cart_list[cart_id]
    cart_list_items[cart_id] = []
    
    return checkout_string
