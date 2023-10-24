from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

#Number of Carts
cart_id = 0
account_id = 0

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """
    previous = ""
    next = ""
    if search_page != "":
        next = search_page
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE account_ledger_entities SET customer_name = :customer_name, item_sku = :potion_sku"))
        result = connection.execute(sqlalchemy.text("SELECT account_ledger_entries.account_id AS line_item_id, account_ledger_entries.item_sku, account_ledger_entries.customer_name, account_transactions.created_at FROM account_ledger_entries JOIN account_transactions ON acount_ledger_entries.id = account_transactions.id GROUP BY :sort_col ORDER BY :sort_order"))
            
    result.update({ "customer_name" : customer_name})
    result.update({ "" : customer_name})
    return {
        "previous": previous,
        "next": next,
        "results": [
            result
        ]
    }


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    cart_id = cart_id + 1
    account_id = account_id + 1
    with db.engine.begin() as connection:
        sql_select_string = connection.execute(sqlalchemy.text("INSERT INTO customer_cart (cart_id, customer, quantity, price, red_count, red_ml, blue_count, blue_ml, green_count, green_ml, dark_count, dark_ml) VALUES (:cart_id, :new_cart.customer, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)"))
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
        sql_select_string = connection.execute(sqlalchemy.text("UPDATE customer_cart SET quantity = :cart_item.quantity WHERE customer_cart.cart_id = :cart_id"))
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE customer_cart SET price = :cart_checkout.payment, checkout? = 1 WHERE customer_cart.cart_id = :cart_id"))
        
        #Ledger
        connection.execute(sqlalchemy.text("INSERT INTO account_transactions (id, description) VALUES (:account_id, 'Paid :cart_checkout.payment')")) 
        connection.execute(sqlalchemy.text("INSERT INTO account_ledger_entries (account_id, change) VALUES (:account_id, - :cart_checkout.payment), (Victor's Bag of Tricks, :cart_checkout.payment);")) 
        return connection.execute(sqlalchemy.text("SELECT quantity AS total_potions_bought, price AS total_gold_paid FROM customer_cart WHERE customer_cart.cart_id = :cart_id"))
    