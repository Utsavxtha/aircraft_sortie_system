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