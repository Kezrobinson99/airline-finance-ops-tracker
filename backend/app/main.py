from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
from .database import Base, engine, get_db, SessionLocal
from . import models, schemas, crud
from .seed_data import seed_database

Base.metadata.create_all(bind=engine)
app=FastAPI(title='Airline Finance & Operations Tracker V4')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup():
    db=SessionLocal(); seed_database(db); db.close()
@app.get('/')
def root(): return {'message':'Airline Tracker V4 API running'}
@app.get('/dashboard')
def dashboard(db:Session=Depends(get_db)): return crud.dashboard(db)
@app.get('/airlines',response_model=list[schemas.AirlineOut])
def airlines(db:Session=Depends(get_db)): return db.query(models.Airline).all()
@app.get('/routes',response_model=list[schemas.RouteOut])
def routes(db:Session=Depends(get_db)): return [crud.route_to_out(r) for r in db.query(models.Route).all()]
@app.get('/aircraft')
def aircraft(db:Session=Depends(get_db)): return [{**a.__dict__,'airline_name':a.airline.name if a.airline else None} for a in db.query(models.Aircraft).all()]
@app.get('/staff')
def staff(db:Session=Depends(get_db)): return [{**s.__dict__,'airline_name':s.airline.name if s.airline else None} for s in db.query(models.Staff).all()]
@app.get('/ground-handling')
def handling(db:Session=Depends(get_db)): return db.query(models.GroundHandling).all()
@app.get('/fuel-prices',response_model=list[schemas.FuelPriceOut])
def fuel(db:Session=Depends(get_db)): return db.query(models.FuelPrice).all()


def calculate_gbp_per_kg(usd_per_barrel: float, usd_to_gbp: float = 0.79, airline_margin: float = 1.08):
    # 42 US gallons per barrel. Jet fuel approx 3.04 kg per US gallon.
    return round((usd_per_barrel / 42 / 3.04) * usd_to_gbp * airline_margin, 3)

@app.post('/fuel-prices/manual', response_model=schemas.FuelPriceOut)
def update_fuel_manual(p: schemas.FuelPriceUpdate, db: Session = Depends(get_db)):
    item = db.query(models.FuelPrice).filter(models.FuelPrice.region == p.region).first()
    if not item:
        item = models.FuelPrice(region=p.region)
        db.add(item)
    item.usd_per_barrel = p.usd_per_barrel
    item.gbp_per_kg = calculate_gbp_per_kg(p.usd_per_barrel, p.usd_to_gbp, p.airline_margin)
    item.notes = f"{p.notes} | USD->GBP {p.usd_to_gbp} | margin {p.airline_margin}"
    db.commit()
    db.refresh(item)
    return item

@app.post('/fuel-prices/mock-live')
def mock_live_fuel_update(db: Session = Depends(get_db)):
    # Simulates real market movements until you plug in an oil/fuel API key.
    import random
    changed = []
    for item in db.query(models.FuelPrice).all():
        movement = random.uniform(-0.045, 0.045)
        item.usd_per_barrel = round(item.usd_per_barrel * (1 + movement), 2)
        item.gbp_per_kg = calculate_gbp_per_kg(item.usd_per_barrel, 0.79, 1.08)
        item.notes = 'Mock live oil/fuel market update - replace with real API later'
        changed.append(item)
    db.commit()
    return [{"region":x.region,"usd_per_barrel":x.usd_per_barrel,"gbp_per_kg":x.gbp_per_kg,"notes":x.notes} for x in changed]

@app.get('/flight-logs',response_model=list[schemas.FlightLogOut])
def logs(db:Session=Depends(get_db)): return [crud.log_to_out(x) for x in db.query(models.FlightLog).order_by(models.FlightLog.date.desc(),models.FlightLog.id.desc()).all()]
@app.post('/flight-logs',response_model=schemas.FlightLogOut)
def post_log(p:schemas.FlightLogCreate,db:Session=Depends(get_db)):
    try: return crud.log_to_out(crud.create_flight_log(db,p))
    except ValueError as e: raise HTTPException(status_code=404,detail=str(e))
@app.post('/flight-logs/simulate',response_model=schemas.FlightLogOut)
def simulate(p:schemas.FlightSimulateCreate,db:Session=Depends(get_db)):
    try: return crud.log_to_out(crud.simulate_flight_log(db,p))
    except ValueError as e: raise HTTPException(status_code=404,detail=str(e))
@app.post('/simulate-day')
def simulate_day(db:Session=Depends(get_db)):
    today=date.today(); routes=db.query(models.Route).all(); made=[]
    for r in routes[:30]: made.append(crud.log_to_out(crud.simulate_flight_log(db,schemas.FlightSimulateCreate(date=today,route_id=r.id))))
    return made
@app.get('/flight-board')
def flight_board(db:Session=Depends(get_db)):
    today=date.today(); rows=db.query(models.FlightLog).filter(models.FlightLog.date==today).order_by(models.FlightLog.scheduled_departure).all()
    if not rows:
        for r in db.query(models.Route).all()[:18]: crud.simulate_flight_log(db,schemas.FlightSimulateCreate(date=today,route_id=r.id))
        rows=db.query(models.FlightLog).filter(models.FlightLog.date==today).order_by(models.FlightLog.scheduled_departure).all()
    return [crud.log_to_out(x) for x in rows]
@app.get('/flight-map')
def flight_map(db:Session=Depends(get_db)): return crud.flight_map(db)
@app.get('/finance/year/{year}')
def fy(year:int,db:Session=Depends(get_db)): return crud.finance_year(db,year)
@app.post('/buy/aircraft')
def buy_aircraft(p:schemas.BuyAircraft,db:Session=Depends(get_db)): return crud.buy_aircraft(db,p)
@app.post('/buy/hub')
def buy_hub(p:schemas.BuyHub,db:Session=Depends(get_db)): return crud.buy_hub(db,p)
@app.post('/buy/route')
def buy_route(p:schemas.BuyRoute,db:Session=Depends(get_db)): return crud.buy_route(db,p)
@app.get('/purchases')
def purchases(db:Session=Depends(get_db)): return db.query(models.Purchase).order_by(models.Purchase.id.desc()).all()


# ---------------- V5 ROUTE/HUB MARKET UPGRADES ----------------

AIRPORT_COORDS = {
    "MAN": (53.365, -2.272), "JFK": (40.641, -73.778), "MCO": (28.431, -81.309),
    "TPA": (27.975, -82.533), "LAS": (36.084, -115.153), "IAH": (29.990, -95.336),
    "LAX": (33.941, -118.408), "DFW": (32.899, -97.040), "ORD": (41.974, -87.907),
    "DEN": (39.856, -104.673), "SEA": (47.450, -122.309), "FLL": (26.072, -80.153),
    "PHL": (39.874, -75.242), "BOS": (42.365, -71.009), "YYZ": (43.677, -79.624),
    "LHR": (51.470, -0.454), "DXB": (25.253, 55.365), "SIN": (1.364, 103.991),
    "AMS": (52.310, 4.768), "BCN": (41.297, 2.083), "FRA": (50.037, 8.562),
    "FCO": (41.800, 12.238), "DUB": (53.421, -6.270), "PMI": (39.551, 2.738),
    "MIA": (25.795, -80.287), "ATL": (33.640, -84.427), "EWR": (40.689, -74.174),
    "SFO": (37.621, -122.379), "SAN": (32.733, -117.193), "PHX": (33.435, -112.010),
}

HUB_MARKET = [
    {"airport":"JFK","name":"New York JFK Hub","purchase_cost":25000000,"monthly_cost":650000,"notes":"Major transatlantic and domestic feed hub"},
    {"airport":"MCO","name":"Orlando Hub","purchase_cost":18000000,"monthly_cost":480000,"notes":"Leisure hub with strong UK/Florida demand"},
    {"airport":"FLL","name":"Fort Lauderdale Hub","purchase_cost":14000000,"monthly_cost":380000,"notes":"South Florida low-cost and Caribbean gateway"},
    {"airport":"DFW","name":"Dallas/Fort Worth Hub","purchase_cost":32000000,"monthly_cost":720000,"notes":"Large central US connection hub"},
    {"airport":"ORD","name":"Chicago O'Hare Hub","purchase_cost":30000000,"monthly_cost":700000,"notes":"Midwest hub and strong domestic feed"},
    {"airport":"DEN","name":"Denver Hub","purchase_cost":22000000,"monthly_cost":510000,"notes":"Mountain/western US connection hub"},
    {"airport":"SEA","name":"Seattle Hub","purchase_cost":21000000,"monthly_cost":500000,"notes":"Pacific Northwest and Asia potential"},
    {"airport":"LAX","name":"Los Angeles Hub","purchase_cost":38000000,"monthly_cost":850000,"notes":"West coast premium hub"},
    {"airport":"DUB","name":"Dublin Hub","purchase_cost":12000000,"monthly_cost":300000,"notes":"EU/UK/US pre-clearance opportunity"},
    {"airport":"VIE","name":"Vienna Hub","purchase_cost":16000000,"monthly_cost":340000,"notes":"Future Lauda Europe central hub"},
    {"airport":"EMA","name":"East Midlands Cargo Hub","purchase_cost":15000000,"monthly_cost":320000,"notes":"Future Monarch Cargo base"},
]

def haversine_nm(origin: str, destination: str):
    import math
    o = AIRPORT_COORDS.get(origin.upper())
    d = AIRPORT_COORDS.get(destination.upper())
    if not o or not d:
        return 750
    lat1, lon1 = map(math.radians, o)
    lat2, lon2 = map(math.radians, d)
    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    km = 6371 * 2 * math.asin(math.sqrt(a))
    return round(km * 0.539957)

def route_quote(origin: str, destination: str):
    origin = origin.upper().strip()
    destination = destination.upper().strip()
    distance = haversine_nm(origin, destination)

    if distance >= 4500:
        aircraft = "A350-1000"
        cost = distance * 7800
        economy = 520
        premium = 1050
        business = 3200
    elif distance >= 2500:
        aircraft = "A330-900"
        cost = distance * 6500
        economy = 390
        premium = 780
        business = 2400
    elif distance >= 900:
        aircraft = "A321neo"
        cost = distance * 5200
        economy = 150
        premium = 300
        business = 0
    else:
        aircraft = "737 MAX 8"
        cost = distance * 4200
        economy = 90
        premium = 180
        business = 0

    # Minimum route-rights values so short sectors are not too cheap.
    cost = max(cost, 750000)
    return {
        "origin": origin,
        "destination": destination,
        "distance_nm": distance,
        "suggested_aircraft": aircraft,
        "route_purchase_cost": round(cost, 0),
        "suggested_economy_price": economy,
        "suggested_premium_price": premium,
        "suggested_business_price": business,
    }

@app.get('/hub-market')
def hub_market(airline_id:int, db:Session=Depends(get_db)):
    owned = {h.airport.upper() for h in db.query(models.Hub).filter(models.Hub.airline_id==airline_id).all()}
    return [h for h in HUB_MARKET if h["airport"].upper() not in owned]

@app.post('/buy/hub-market')
def buy_hub_market(payload:dict, db:Session=Depends(get_db)):
    airline_id = int(payload.get("airline_id"))
    airport = payload.get("airport","").upper()
    option = next((h for h in HUB_MARKET if h["airport"] == airport), None)
    if not option:
        raise HTTPException(status_code=404, detail="Hub option not found")
    return crud.buy_hub(db, schemas.BuyHub(
        airline_id=airline_id,
        airport=option["airport"],
        name=option["name"],
        purchase_cost=option["purchase_cost"],
        monthly_cost=option["monthly_cost"],
    ))

@app.post('/route/quote')
def quote_route(p:schemas.RouteQuoteRequest, db:Session=Depends(get_db)):
    quote = route_quote(p.origin, p.destination)
    airline = db.query(models.Airline).filter(models.Airline.id==p.airline_id).first()
    quote["airline_id"] = p.airline_id
    quote["airline_code"] = airline.code if airline else "XX"
    return quote

@app.post('/buy/custom-route')
def buy_custom_route(p:schemas.CustomRouteBuy, db:Session=Depends(get_db)):
    quote = route_quote(p.origin, p.destination)
    airline = db.query(models.Airline).filter(models.Airline.id==p.airline_id).first()
    if not airline:
        raise HTTPException(status_code=404, detail="Airline not found")
    prefix = airline.code if airline else "XX"
    import random
    fn = p.flight_number or f"{prefix}{random.randint(100,899)}"
    rfn = p.return_flight_number or f"{prefix}{random.randint(900,999)}"
    return crud.buy_route(db, schemas.BuyRoute(
        airline_id=p.airline_id,
        flight_number=fn,
        return_flight_number=rfn,
        origin=quote["origin"],
        destination=quote["destination"],
        aircraft_type=p.aircraft_type or quote["suggested_aircraft"],
        distance_nm=quote["distance_nm"],
        economy_price=p.economy_price or quote["suggested_economy_price"],
        premium_price=p.premium_price or quote["suggested_premium_price"],
        business_price=p.business_price if p.business_price is not None else quote["suggested_business_price"],
        purchase_cost=quote["route_purchase_cost"],
    ))

@app.patch('/routes/{route_id}/aircraft')
def update_route_aircraft(route_id:int, p:schemas.RouteAircraftUpdate, db:Session=Depends(get_db)):
    route = db.query(models.Route).filter(models.Route.id==route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    route.aircraft_type = p.aircraft_type
    db.commit()
    db.refresh(route)
    return crud.route_to_out(route)
