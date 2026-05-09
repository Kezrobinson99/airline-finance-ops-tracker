from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Airline(Base):
    __tablename__ = "airlines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=False, unique=True)
    region = Column(String, nullable=False)
    bank_balance = Column(Float, default=0)
    routes = relationship("Route", back_populates="airline")
    aircraft = relationship("Aircraft", back_populates="airline")
    staff = relationship("Staff", back_populates="airline")

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    flight_number = Column(String, nullable=False)
    return_flight_number = Column(String, nullable=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    aircraft_type = Column(String, nullable=False)
    frequency = Column(String, default="Daily")
    distance_nm = Column(Float, default=500)
    economy_price = Column(Float, default=150)
    premium_price = Column(Float, default=450)
    business_price = Column(Float, default=1200)
    load_factor = Column(Float, default=82)
    handling_cost = Column(Float, default=0)
    crew_cost = Column(Float, default=0)
    catering_cost = Column(Float, default=0)
    maintenance_cost = Column(Float, default=0)
    purchase_cost = Column(Float, default=0)
    is_owned = Column(Integer, default=1)
    airline = relationship("Airline", back_populates="routes")
    flight_logs = relationship("FlightLog", back_populates="route")

class Aircraft(Base):
    __tablename__ = "aircraft"
    id = Column(Integer, primary_key=True, index=True)
    registration = Column(String, nullable=False, unique=True)
    aircraft_type = Column(String, nullable=False)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    purchase_price = Column(Float, default=0)
    lease_cost_monthly = Column(Float, default=0)
    fuel_burn_per_hour = Column(Float, default=0)
    maintenance_cost_per_flight = Column(Float, default=0)
    status = Column(String, default="active")
    assigned_route = Column(String, default="")
    daily_utilisation_hours = Column(Float, default=0)
    is_owned = Column(Integer, default=1)
    airline = relationship("Airline", back_populates="aircraft")
    flight_logs = relationship("FlightLog", back_populates="aircraft")

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    count = Column(Integer, default=0)
    salary_cost_monthly = Column(Float, default=0)
    department = Column(String, nullable=False)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    base = Column(String, nullable=False)
    airline = relationship("Airline", back_populates="staff")

class GroundHandling(Base):
    __tablename__ = "ground_handling"
    id = Column(Integer, primary_key=True, index=True)
    airport = Column(String, nullable=False)
    handling_agent = Column(String, nullable=False)
    cost_per_turn = Column(Float, default=0)
    annual_contract_value = Column(Float, default=0)
    performance_rating = Column(Float, default=8.0)
    delay_incidents = Column(Integer, default=0)
    notes = Column(Text, default="")

class Hub(Base):
    __tablename__ = "hubs"
    id = Column(Integer, primary_key=True, index=True)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    airport = Column(String, nullable=False)
    name = Column(String, nullable=False)
    purchase_cost = Column(Float, default=0)
    monthly_cost = Column(Float, default=0)
    is_owned = Column(Integer, default=1)

class FuelPrice(Base):
    __tablename__ = "fuel_prices"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, nullable=False, unique=True)
    usd_per_barrel = Column(Float, default=181.22)
    gbp_per_kg = Column(Float, default=1.12)
    notes = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    item_type = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    cost = Column(Float, default=0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class FlightLog(Base):
    __tablename__ = "flight_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    flight_number = Column(String, nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=True)
    scheduled_departure = Column(String, default="09:00")
    scheduled_arrival = Column(String, default="12:00")
    status = Column(String, default="Scheduled")
    progress_percent = Column(Float, default=0)
    passengers_carried = Column(Integer, default=0)
    average_fare = Column(Float, default=0)
    ancillary_revenue = Column(Float, default=0)
    fuel_price = Column(Float, default=1.12)
    delay_minutes = Column(Integer, default=0)
    extra_costs = Column(Float, default=0)
    fuel_kg = Column(Float, default=0)
    block_hours = Column(Float, default=0)
    delay_cost = Column(Float, default=0)
    passenger_revenue = Column(Float, default=0)
    total_revenue = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    profit_loss = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    route = relationship("Route", back_populates="flight_logs")
    aircraft = relationship("Aircraft", back_populates="flight_logs")
