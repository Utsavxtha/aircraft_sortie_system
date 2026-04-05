from sqlalchemy import Column, String, Date, Time, Numeric, ForeignKey, DateTime
from database.connection import Base

class Aircraft(Base):
    __tablename__ = "aircraft"
    aircraft_id = Column(String(50), primary_key=True)
    registration_number = Column(String(50), unique=True)
    model = Column(String(100))
    type = Column(String(50))
    status = Column(String(50))
    flight_hours_total = Column(Numeric(10, 2))
    last_maintenance_date = Column(Date)

class Pilot(Base):
    __tablename__ = "pilot"
    pilot_id = Column(String(50), primary_key=True)
    badge_number = Column(String(50), unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    rank = Column(String(50))
    qualification_level = Column(String(50))
    status = Column(String(50))
    flight_hours_month = Column(Numeric(10, 2))
    flight_hours_total = Column(Numeric(10, 2))

class Flight(Base):
    __tablename__ = "flight"
    flight_id = Column(String(50), primary_key=True)
    flight_number = Column(String(50), unique=True)
    call_sign = Column(String(50))
    aircraft_id = Column(String(50), ForeignKey("aircraft.aircraft_id"))
    flight_date = Column(Date)
    estimated_departure = Column(Time)
    estimated_arrival = Column(Time)
    actual_departure = Column(Time)
    actual_arrival = Column(Time)
    flight_purpose = Column(String(200))
    flight_plan = Column(String(500))
    status = Column(String(50))
    flight_duration = Column(Numeric(10, 2))
    mission_type = Column(String(100))

class Crew(Base):
    __tablename__ = "crew"
    crew_id = Column(String(50), primary_key=True)
    flight_id = Column(String(50), ForeignKey("flight.flight_id"))
    pilot_id = Column(String(50), ForeignKey("pilot.pilot_id"))
    role = Column(String(100))
    duty_station = Column(String(100))

class FlightLog(Base):
    __tablename__ = "flight_log"
    log_id = Column(String(50), primary_key=True)
    flight_id = Column(String(50), ForeignKey("flight.flight_id"))
    log_time = Column(DateTime)
    log_type = Column(String(100))
    description = Column(String(500))
    location = Column(String(200))
    fuel_remaining = Column(Numeric(10, 2))

class Passenger(Base):
    __tablename__ = "passenger"
    passenger_id = Column(String(50), primary_key=True)
    ticket_number = Column(String(50), unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    class_ = Column("class", String(50))
    status = Column(String(50))
    passport_number = Column(String(100))

class Booking(Base):
    __tablename__ = "booking"
    booking_id = Column(String(50), primary_key=True)
    flight_id = Column(String(50), ForeignKey("flight.flight_id"))
    passenger_id = Column(String(50), ForeignKey("passenger.passenger_id"))
    booking_date = Column(Date)
    seat_assignment = Column(String(20))
    booking_status = Column(String(50))