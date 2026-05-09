from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
import random, math
from . import models, schemas

AIRPORTS={"MAN":(53.365,-2.272),"LHR":(51.470,-0.454),"SIN":(1.364,103.991),"DXB":(25.253,55.365),"TPA":(27.975,-82.533),"YYZ":(43.677,-79.624),"BOS":(42.365,-71.009),"PMI":(39.552,2.738),"AMS":(52.310,4.768),"BCN":(41.297,2.078),"FRA":(50.037,8.562),"FCO":(41.800,12.238),"DUB":(53.421,-6.270),"IAH":(29.990,-95.336),"JFK":(40.641,-73.778),"MCO":(28.431,-81.309),"LAS":(36.084,-115.153),"LAX":(33.942,-118.408),"DFW":(32.899,-97.040),"ORD":(41.974,-87.907),"DEN":(39.856,-104.673),"SEA":(47.450,-122.309),"FLL":(26.074,-80.152),"PHL":(39.874,-75.242),"New York":(40.641,-73.778)}

def route_to_out(route):
    seats = seats_for_type(route.aircraft_type)
    avg=(route.economy_price*.75)+(route.premium_price*.18)+(route.business_price*.07)
    rev=seats*(route.load_factor/100)*avg
    cost=route.handling_cost+route.crew_cost+route.catering_cost+route.maintenance_cost+(route.distance_nm*12)
    return schemas.RouteOut(id=route.id,airline_id=route.airline_id,airline_name=route.airline.name if route.airline else None,flight_number=route.flight_number,return_flight_number=route.return_flight_number,origin=route.origin,destination=route.destination,aircraft_type=route.aircraft_type,frequency=route.frequency,distance_nm=route.distance_nm,economy_price=route.economy_price,premium_price=route.premium_price,business_price=route.business_price,load_factor=route.load_factor,handling_cost=route.handling_cost,crew_cost=route.crew_cost,catering_cost=route.catering_cost,maintenance_cost=route.maintenance_cost,purchase_cost=route.purchase_cost,is_owned=route.is_owned,estimated_revenue=round(rev,2),estimated_cost=round(cost,2),estimated_profit=round(rev-cost,2))

def seats_for_type(t):
    if 'A350' in t: return 350
    if 'A340' in t: return 320
    if 'A330' in t: return 290
    if 'A321' in t: return 210
    if '737' in t: return 186
    return 180

def block_hours(route, aircraft):
    speed=440 if aircraft and ('737' in aircraft.aircraft_type or 'A321' in aircraft.aircraft_type) else 480
    return round((route.distance_nm/speed)+0.75,2)

def fuel_kg(route, aircraft):
    burn=aircraft.fuel_burn_per_hour if aircraft else (2500 if route.distance_nm<1200 else 5600)
    bh=block_hours(route,aircraft)
    return round(burn*bh*1.08,0), bh

def delay_minutes(route):
    x=random.random()-(0.06 if route.distance_nm>2800 else 0)-(0.04 if route.destination in ['MCO','TPA','PMI','LAS'] else 0)
    if x<0.04: return random.randint(95,240)
    if x<0.12: return random.randint(30,94)
    if x<0.30: return random.randint(8,29)
    return 0

def delay_cost(mins,pax,aircraft):
    wide=aircraft and any(a in aircraft.aircraft_type for a in ['A330','A340','A350'])
    base=mins*(95 if wide else 55)
    if mins>=180: base+=pax*220
    elif mins>=120: base+=pax*45
    return round(base,2)

def times_for(route_id, bh, delay):
    dep_hour=6+(route_id*2)%15
    dep_min=(route_id*7)%60
    arr=dep_hour+bh+(delay/60)
    ah=int(arr)%24; am=int((arr-int(arr))*60)
    return f'{dep_hour:02d}:{dep_min:02d}', f'{ah:02d}:{am:02d}'

def status_for(delay):
    if delay>=120: return 'Major Delay'
    if delay>=30: return 'Delayed'
    if delay>0: return 'Late'
    return random.choice(['On Time','Boarding','Departed','In Air'])

def create_flight_log(db:Session,payload:schemas.FlightLogCreate):
    route=db.query(models.Route).filter(models.Route.id==payload.route_id).first()
    if not route: raise ValueError('Route not found')
    aircraft=db.query(models.Aircraft).filter(models.Aircraft.id==payload.aircraft_id).first() if payload.aircraft_id else None
    fkg,bh=fuel_kg(route,aircraft); fcost=fkg*payload.fuel_price; dcost=delay_cost(payload.delay_minutes,payload.passengers_carried,aircraft)
    rev=payload.passengers_carried*payload.average_fare+payload.ancillary_revenue
    cost=fcost+route.handling_cost+route.crew_cost+route.catering_cost+route.maintenance_cost+dcost+payload.extra_costs
    dep,arr=times_for(route.id,bh,payload.delay_minutes)
    log=models.FlightLog(**payload.model_dump(),scheduled_departure=dep,scheduled_arrival=arr,status=status_for(payload.delay_minutes),progress_percent=random.randint(15,95),fuel_kg=fkg,block_hours=bh,delay_cost=dcost,passenger_revenue=round(payload.passengers_carried*payload.average_fare,2),total_revenue=round(rev,2),total_cost=round(cost,2),profit_loss=round(rev-cost,2))
    db.add(log); db.commit(); db.refresh(log); return log

def simulate_flight_log(db:Session,payload:schemas.FlightSimulateCreate):
    route=db.query(models.Route).filter(models.Route.id==payload.route_id).first()
    if not route: raise ValueError('Route not found')
    aircraft=db.query(models.Aircraft).filter(models.Aircraft.id==payload.aircraft_id).first() if payload.aircraft_id else db.query(models.Aircraft).filter(models.Aircraft.airline_id==route.airline_id,models.Aircraft.status=='active').first()
    fuel=db.query(models.FuelPrice).filter(models.FuelPrice.region==payload.fuel_region).first() or db.query(models.FuelPrice).first()
    seats=seats_for_type(route.aircraft_type); lf=max(55,min(98,random.gauss(route.load_factor,6))); pax=int(seats*(lf/100))
    avg=(route.economy_price*random.uniform(.72,.92))+(route.premium_price*random.uniform(.10,.20))+(route.business_price*random.uniform(.03,.08))
    if route.business_price==0: avg=route.economy_price*random.uniform(.90,1.25)
    delay=payload.force_delay_minutes if payload.force_delay_minutes is not None else delay_minutes(route)
    return create_flight_log(db,schemas.FlightLogCreate(date=payload.date,flight_number=route.flight_number,route_id=route.id,aircraft_id=aircraft.id if aircraft else None,passengers_carried=pax,average_fare=round(avg,2),ancillary_revenue=round(pax*random.uniform(18,45),2),fuel_price=fuel.gbp_per_kg if fuel else 1.12,delay_minutes=delay,extra_costs=0))

def log_to_out(log):
    return schemas.FlightLogOut(id=log.id,date=log.date,flight_number=log.flight_number,route_id=log.route_id,aircraft_id=log.aircraft_id,scheduled_departure=log.scheduled_departure,scheduled_arrival=log.scheduled_arrival,status=log.status,progress_percent=log.progress_percent,passengers_carried=log.passengers_carried,average_fare=log.average_fare,ancillary_revenue=log.ancillary_revenue,fuel_price=log.fuel_price,delay_minutes=log.delay_minutes,extra_costs=log.extra_costs,fuel_kg=log.fuel_kg,block_hours=log.block_hours,delay_cost=log.delay_cost,passenger_revenue=log.passenger_revenue,total_revenue=log.total_revenue,total_cost=log.total_cost,profit_loss=log.profit_loss,route_name=f'{log.route.origin}-{log.route.destination}' if log.route else None,origin=log.route.origin if log.route else None,destination=log.route.destination if log.route else None,aircraft_registration=log.aircraft.registration if log.aircraft else None)

def dashboard(db:Session):
    today=date.today(); ws=today-timedelta(days=today.weekday()); ms=today.replace(day=1); ys=today.replace(month=1,day=1)
    def totals(start):
        rows=db.query(models.FlightLog).filter(models.FlightLog.date>=start).all(); return {'revenue':round(sum(x.total_revenue for x in rows),2),'costs':round(sum(x.total_cost for x in rows),2),'profit':round(sum(x.profit_loss for x in rows),2)}
    todays=db.query(models.FlightLog).filter(models.FlightLog.date==today).all()
    purchases=sum(x.cost for x in db.query(models.Purchase).all())
    group=sum(a.bank_balance for a in db.query(models.Airline).all())+sum(x.profit_loss for x in db.query(models.FlightLog).all())-purchases
    alerts=[]; fuel=db.query(models.FuelPrice).filter(models.FuelPrice.region=='Global').first()
    if fuel and fuel.gbp_per_kg>=1.1: alerts.append(f'Fuel price spike watch: Global planning fuel is £{fuel.gbp_per_kg:.2f}/kg.')
    delays=db.query(models.FlightLog).filter(models.FlightLog.delay_minutes>=30).count()
    if delays: alerts.append(f'{delays} flight logs have delays of 30+ minutes.')
    alerts.append('Flight map, daily board and purchasing system online.')
    airlines=[]
    for a in db.query(models.Airline).all():
        logs=db.query(models.FlightLog).join(models.Route).filter(models.Route.airline_id==a.id).all(); pur=sum(p.cost for p in db.query(models.Purchase).filter(models.Purchase.airline_id==a.id).all())
        profit=sum(x.profit_loss for x in logs); airlines.append({'name':a.name,'code':a.code,'bank_balance':round(a.bank_balance+profit-pur,2),'revenue':round(sum(x.total_revenue for x in logs),2),'costs':round(sum(x.total_cost for x in logs)+pur,2),'profit':round(profit-pur,2)})
    return {'group_bank_balance':round(group,2),'today':{'revenue':round(sum(x.total_revenue for x in todays),2),'costs':round(sum(x.total_cost for x in todays),2),'profit':round(sum(x.profit_loss for x in todays),2)},'weekly':totals(ws),'monthly':totals(ms),'yearly':totals(ys),'route_count':db.query(models.Route).count(),'aircraft_count':db.query(models.Aircraft).count(),'staff_count':int(db.query(func.sum(models.Staff.count)).scalar() or 0),'alerts':alerts,'airlines':airlines}

def finance_year(db:Session,year:int):
    rows=db.query(models.FlightLog).filter(models.FlightLog.date>=date(year,1,1),models.FlightLog.date<=date(year,12,31)).all(); purchases=db.query(models.Purchase).filter(models.Purchase.date>=date(year,1,1),models.Purchase.date<=date(year,12,31)).all()
    months=[]
    for m in range(1,13):
        r=[x for x in rows if x.date.month==m]; p=[x for x in purchases if x.date.month==m]
        months.append({'month':m,'revenue':round(sum(x.total_revenue for x in r),2),'operating_cost':round(sum(x.total_cost for x in r),2),'purchases':round(sum(x.cost for x in p),2),'profit':round(sum(x.profit_loss for x in r)-sum(x.cost for x in p),2)})
    return {'year':year,'revenue':round(sum(x.total_revenue for x in rows),2),'operating_cost':round(sum(x.total_cost for x in rows),2),'purchases':round(sum(x.cost for x in purchases),2),'profit':round(sum(x.profit_loss for x in rows)-sum(x.cost for x in purchases),2),'months':months}

def flight_map(db:Session):
    logs=db.query(models.FlightLog).order_by(models.FlightLog.id.desc()).limit(60).all(); out=[]
    for l in logs:
        o=AIRPORTS.get(l.route.origin,(0,0)); d=AIRPORTS.get(l.route.destination,(0,0)); p=l.progress_percent/100
        out.append({'id':l.id,'flight_number':l.flight_number,'route':f'{l.route.origin}-{l.route.destination}','status':l.status,'progress':l.progress_percent,'origin':l.route.origin,'destination':l.route.destination,'origin_lat':o[0],'origin_lon':o[1],'dest_lat':d[0],'dest_lon':d[1],'lat':o[0]+(d[0]-o[0])*p,'lon':o[1]+(d[1]-o[1])*p,'profit_loss':l.profit_loss})
    return out

def buy_aircraft(db:Session,p:schemas.BuyAircraft):
    a=db.query(models.Airline).filter(models.Airline.id==p.airline_id).first();
    item=models.Aircraft(registration=p.registration,aircraft_type=p.aircraft_type,airline_id=p.airline_id,purchase_price=p.purchase_price,fuel_burn_per_hour=p.fuel_burn_per_hour,maintenance_cost_per_flight=p.maintenance_cost_per_flight,status='active',is_owned=1)
    db.add(item); db.add(models.Purchase(date=date.today(),airline_id=p.airline_id,item_type='Aircraft',item_name=f'{p.registration} {p.aircraft_type}',cost=p.purchase_price,notes='Aircraft purchase'))
    db.commit(); return item

def buy_hub(db:Session,p:schemas.BuyHub):
    item=models.Hub(airline_id=p.airline_id,airport=p.airport,name=p.name,purchase_cost=p.purchase_cost,monthly_cost=p.monthly_cost,is_owned=1)
    db.add(item); db.add(models.Purchase(date=date.today(),airline_id=p.airline_id,item_type='Hub',item_name=f'{p.airport} {p.name}',cost=p.purchase_cost,notes='Hub purchase'))
    db.commit(); return item

def buy_route(db:Session,p:schemas.BuyRoute):
    item=models.Route(airline_id=p.airline_id,flight_number=p.flight_number,return_flight_number=p.return_flight_number,origin=p.origin,destination=p.destination,aircraft_type=p.aircraft_type,distance_nm=p.distance_nm,economy_price=p.economy_price,premium_price=p.premium_price,business_price=p.business_price,purchase_cost=p.purchase_cost,is_owned=1,load_factor=74,handling_cost=4500,crew_cost=6000,catering_cost=2200,maintenance_cost=3000)
    db.add(item); db.add(models.Purchase(date=date.today(),airline_id=p.airline_id,item_type='Route',item_name=f'{p.origin}-{p.destination}',cost=p.purchase_cost,notes='Route rights purchase'))
    db.commit(); return item
