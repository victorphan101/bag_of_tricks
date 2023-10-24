from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    with db.engine.begin() as connection:
        return connection.execute(sqlalchemy.text("SELECT SUM(num_red_potions, num_blue_potions, num_green_potions) AS number_of_potions, SUM(num_red_ml, num_blue_ml, num_green_ml) AS ml_in_barrels, gold from global_inventory"))


class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
