import customtkinter as ctk
from database.connection import Base, engine, get_session
from views.aircraft_view import AircraftView
from views.flight_view import FlightView
from views.pilot_view import PilotView
from views.crew_view import CrewView
from views.flight_log_view import FlightLogView
from views.booking_view import BookingView
from views.passenger_view import PassengerView
from views.query_view import QueryView

Base.metadata.create_all(engine)

from database.models import Aircraft, Pilot, Flight, Crew, FlightLog, Passenger, Booking
from database.connection import get_session

def seed():
    s = get_session()
    if s.query(Aircraft).count() > 0:
        return  # already seeded

    s.add_all([
        Aircraft(aircraft_id="AC001", registration_number="REG-001", model="F-16 Falcon",     type="Fighter",    status="Active",      flight_hours_total=1200.50, last_maintenance_date="2024-12-01"),
        Aircraft(aircraft_id="AC002", registration_number="REG-002", model="C-130 Hercules",  type="Transport",  status="Active",      flight_hours_total=3400.00, last_maintenance_date="2025-01-15"),
        Aircraft(aircraft_id="AC003", registration_number="REG-003", model="Apache AH-64",    type="Helicopter", status="Maintenance", flight_hours_total=890.75,  last_maintenance_date="2025-03-10"),
    ])
    s.add_all([
        Pilot(pilot_id="P001", badge_number="B-101", first_name="Rajesh", last_name="Sharma", rank="Squadron Leader",    qualification_level="Level 3", status="Active", flight_hours_month=45.5,  flight_hours_total=1200.0),
        Pilot(pilot_id="P002", badge_number="B-102", first_name="Anita",  last_name="Thapa",  rank="Flight Lieutenant", qualification_level="Level 2", status="Active", flight_hours_month=38.0,  flight_hours_total=980.5),
        Pilot(pilot_id="P003", badge_number="B-103", first_name="Bikash", last_name="Rai",    rank="Wing Commander",    qualification_level="Level 4", status="Active", flight_hours_month=52.0,  flight_hours_total=2100.0),
    ])
    s.add_all([
        Flight(flight_id="FL001", flight_number="FN-2025-001", call_sign="EAGLE1", aircraft_id="AC001", flight_date="2025-06-01", estimated_departure="06:00:00", estimated_arrival="08:00:00", actual_departure="06:05:00", actual_arrival="08:10:00", flight_purpose="Training",           flight_plan="Route A to B", status="Completed", flight_duration=2.08, mission_type="Training"),
        Flight(flight_id="FL002", flight_number="FN-2025-002", call_sign="HAWK2",  aircraft_id="AC002", flight_date="2025-06-03", estimated_departure="09:00:00", estimated_arrival="13:00:00", actual_departure="09:15:00", actual_arrival="13:10:00", flight_purpose="Logistics",          flight_plan="Route C to D", status="Completed", flight_duration=3.92, mission_type="Logistics"),
        Flight(flight_id="FL003", flight_number="FN-2025-003", call_sign="VIPER3", aircraft_id="AC001", flight_date="2025-06-10", estimated_departure="14:00:00", estimated_arrival="16:00:00", actual_departure=None,        actual_arrival=None,        flight_purpose="Combat Air Patrol", flight_plan="Route E",      status="Scheduled", flight_duration=2.00, mission_type="Combat"),
    ])
    s.add_all([
        Crew(crew_id="CR001", flight_id="FL001", pilot_id="P001", role="Pilot in Command", duty_station="Cockpit"),
        Crew(crew_id="CR002", flight_id="FL001", pilot_id="P002", role="Co-Pilot",         duty_station="Cockpit"),
        Crew(crew_id="CR003", flight_id="FL002", pilot_id="P003", role="Pilot in Command", duty_station="Cockpit"),
        Crew(crew_id="CR004", flight_id="FL003", pilot_id="P001", role="Pilot in Command", duty_station="Cockpit"),
    ])
    s.add_all([
        FlightLog(log_id="LOG001", flight_id="FL001", log_time="2025-06-01 06:05:00", log_type="Departure", description="Takeoff successful",        location="Runway 09L",   fuel_remaining=4500.00),
        FlightLog(log_id="LOG002", flight_id="FL001", log_time="2025-06-01 07:00:00", log_type="Waypoint",  description="Passing waypoint Alpha",    location="Grid 45N-83E", fuel_remaining=3800.00),
        FlightLog(log_id="LOG003", flight_id="FL001", log_time="2025-06-01 08:10:00", log_type="Arrival",   description="Landed successfully",       location="Runway 27R",   fuel_remaining=1200.00),
        FlightLog(log_id="LOG004", flight_id="FL002", log_time="2025-06-03 09:15:00", log_type="Departure", description="Takeoff successful",        location="Runway 18L",   fuel_remaining=8000.00),
    ])
    s.add_all([
        Passenger(passenger_id="PAS001", ticket_number="TKT-001", first_name="Suyog", last_name="Bhandari", class_="Business", status="Active", passport_number="NP-12345"),
        Passenger(passenger_id="PAS002", ticket_number="TKT-002", first_name="Ujwol", last_name="Acharya",  class_="Economy",  status="Active", passport_number="NP-67890"),
        Passenger(passenger_id="PAS003", ticket_number="TKT-003", first_name="Hari",  last_name="Gurung",   class_="Economy",  status="Active", passport_number="NP-11223"),
    ])
    s.add_all([
        Booking(booking_id="BK001", flight_id="FL002", passenger_id="PAS001", booking_date="2025-05-20", seat_assignment="12A", booking_status="Confirmed"),
        Booking(booking_id="BK002", flight_id="FL002", passenger_id="PAS002", booking_date="2025-05-21", seat_assignment="14B", booking_status="Confirmed"),
        Booking(booking_id="BK003", flight_id="FL003", passenger_id="PAS003", booking_date="2025-05-25", seat_assignment="10C", booking_status="Pending"),
    ])
    s.commit()

seed()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aircraft Sortie Management System")
        self.geometry("1200x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="✈ ASMS", font=("Arial", 18, "bold")).pack(pady=20)

        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self.current_view = None

        nav_items = [
            ("🛩  Aircraft",    AircraftView),
            ("👨‍✈️  Pilots",      PilotView),
            ("🛫  Flights",     FlightView),
            ("👥  Crew",        CrewView),
            ("📋  Flight Logs", FlightLogView),
            ("🎫  Bookings",    BookingView),
            ("🧳  Passengers",  PassengerView),
            ("🖥  SQL Console", QueryView),
        ]

        for label, view_class in nav_items:
            ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                command=lambda vc=view_class: self.show_view(vc)
            ).pack(fill="x", padx=10, pady=4)

        self.show_view(AircraftView)

    def show_view(self, view_class):
        # Expire all ORM objects so next view gets fresh data
        get_session().expire_all()

        if self.current_view is not None:
            self.current_view.destroy()

        self.current_view = view_class(self.content)
        self.current_view.pack(fill="both", expand=True)

    def on_close(self):
        try:
            get_session().close()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()