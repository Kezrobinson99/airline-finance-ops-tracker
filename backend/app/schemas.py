from pydantic import BaseModel
from datetime import date
from typing import Optional

class AirlineOut(BaseModel):
    id:int; name:str; code:str; region:str; bank_balance:float
    class Config: from_attributes=True

class RouteOut(BaseModel):
    id:int; airline_id:int; airline_name:Optional[str]=None; flight_number:str; return_flight_number:Optional[str]=None
    origin:str; destination:str; aircraft_type:str; frequency:str; distance_nm:float
    economy_price:float; premium_price:float; business_price:float; load_factor:float
    handling_cost:float; crew_cost:float; catering_cost:float; maintenance_cost:float; purchase_cost:float=0; is_owned:int=1
    estimated_revenue:float=0; estimated_cost:float=0; estimated_profit:float=0
    class Config: from_attributes=True

class FlightLogCreate(BaseModel):
    date:date; flight_number:str; route_id:int; aircraft_id:Optional[int]=None
    passengers_carried:int; average_fare:float; ancillary_revenue:float=0; fuel_price:float=1.12
    delay_minutes:int=0; extra_costs:float=0

class FlightSimulateCreate(BaseModel):
    date:date; route_id:int; aircraft_id:Optional[int]=None; fuel_region:str="Global"; force_delay_minutes:Optional[int]=None

class FlightLogOut(BaseModel):
    id:int; date:date; flight_number:str; route_id:int; aircraft_id:Optional[int]=None
    scheduled_departure:str; scheduled_arrival:str; status:str; progress_percent:float
    passengers_carried:int; average_fare:float; ancillary_revenue:float; fuel_price:float; delay_minutes:int; extra_costs:float
    fuel_kg:float; block_hours:float; delay_cost:float; passenger_revenue:float; total_revenue:float; total_cost:float; profit_loss:float
    route_name:Optional[str]=None; origin:Optional[str]=None; destination:Optional[str]=None; aircraft_registration:Optional[str]=None
    class Config: from_attributes=True

class BuyAircraft(BaseModel):
    airline_id:int; registration:str; aircraft_type:str; purchase_price:float; fuel_burn_per_hour:float; maintenance_cost_per_flight:float=2500

class BuyHub(BaseModel):
    airline_id:int; airport:str; name:str; purchase_cost:float; monthly_cost:float=0

class BuyRoute(BaseModel):
    airline_id:int; flight_number:str; return_flight_number:Optional[str]=None; origin:str; destination:str; aircraft_type:str
    distance_nm:float; economy_price:float=120; premium_price:float=250; business_price:float=0; purchase_cost:float=500000

class FuelPriceOut(BaseModel):
    id:int; region:str; usd_per_barrel:float; gbp_per_kg:float; notes:str
    class Config: from_attributes=True


class FuelPriceUpdate(BaseModel):
    region: str = "Global"
    usd_per_barrel: float = 181.22
    usd_to_gbp: float = 0.79
    airline_margin: float = 1.08
    notes: str = "Manual market update"


class RouteQuoteRequest(BaseModel):
    airline_id:int
    origin:str
    destination:str

class CustomRouteBuy(BaseModel):
    airline_id:int
    origin:str
    destination:str
    aircraft_type:str="A321neo"
    economy_price:float=140
    premium_price:float=280
    business_price:float=0
    flight_number:Optional[str]=None
    return_flight_number:Optional[str]=None

class RouteAircraftUpdate(BaseModel):
    aircraft_type:str
