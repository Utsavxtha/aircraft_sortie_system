import customtkinter as ctk
from database.connection import get_session
from database.models import Booking, Flight, Passenger
import uuid
from database.utils import safe_delete


LABEL_FONT = ("Arial", 12)
ENTRY_WIDTH = 300


def make_field(parent, label, row, values=None):
    ctk.CTkLabel(parent, text=label, font=LABEL_FONT, anchor="w").grid(
        row=row, column=0, sticky="w", padx=(10, 5), pady=5
    )
    if values:
        widget = ctk.CTkOptionMenu(parent, values=values, width=ENTRY_WIDTH)
    else:
        widget = ctk.CTkEntry(parent, width=ENTRY_WIDTH)
    widget.grid(row=row, column=1, sticky="w", padx=(0, 10), pady=5)
    return widget


class BookingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = get_session()
        self.selected_id = None
        self.build_ui()
        self.load_bookings()

    def build_ui(self):
        ctk.CTkLabel(self, text="🎫  Booking Management", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=5)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        form_outer = ctk.CTkFrame(main)
        form_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(form_outer, text="Add / Edit Booking", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        form = ctk.CTkFrame(form_outer, fg_color="transparent")
        form.pack(padx=10, pady=5, fill="x")

        flight_ids    = [f.flight_id    for f in self.session.query(Flight).all()]    or ["None"]
        passenger_ids = [p.passenger_id for p in self.session.query(Passenger).all()] or ["None"]

        self.f_flight    = make_field(form, "Flight ID",              0, flight_ids)
        self.f_passenger = make_field(form, "Passenger ID",           1, passenger_ids)
        self.f_date      = make_field(form, "Booking Date (YYYY-MM-DD)", 2)
        self.f_seat      = make_field(form, "Seat Assignment",        3)
        self.f_status    = make_field(form, "Booking Status",         4, ["Confirmed", "Pending", "Cancelled", "Waitlisted"])

        btn_frame = ctk.CTkFrame(form_outer, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="➕ Add",    width=90, command=self.add_booking).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Update", width=90, command=self.update_booking, fg_color="#2a7d4f").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑 Delete", width=90, command=self.delete_booking, fg_color="#a33").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Clear",  width=90, command=self.clear_form,     fg_color="gray").pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(form_outer, text="", font=("Arial", 11), text_color="gray")
        self.status_label.pack(pady=(0, 10))

        list_outer = ctk.CTkFrame(main)
        list_outer.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(list_outer, text="Booking List", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkButton(list_outer, text="🔄 Refresh", command=self.load_bookings, width=100).pack(pady=(0, 5))
        self.listbox = ctk.CTkTextbox(list_outer, font=("Courier", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.listbox.bind("<ButtonRelease-1>", self.on_select)

    def load_bookings(self):
        self.booking_data = self.session.query(Booking).all()
        self.listbox.delete("1.0", "end")
        header = f"{'ID':<8}  {'Flight':<8}  {'Passenger':<12}  {'Date':<12}  {'Seat':<6}  {'Status'}\n"
        self.listbox.insert("end", header)
        self.listbox.insert("end", "-" * 70 + "\n")
        for b in self.booking_data:
            self.listbox.insert("end", f"{b.booking_id:<8}  {b.flight_id:<8}  {b.passenger_id:<12}  {str(b.booking_date):<12}  {b.seat_assignment:<6}  {b.booking_status}\n")

    def on_select(self, event):
        try:
            index = int(self.listbox.index("insert").split(".")[0]) - 3
            if 0 <= index < len(self.booking_data):
                b = self.booking_data[index]
                self.selected_id = b.booking_id
                self._clear_fields()
                self.f_flight.set(b.flight_id)
                self.f_passenger.set(b.passenger_id)
                self.f_date.insert(0, str(b.booking_date or ""))
                self.f_seat.insert(0, b.seat_assignment or "")
                self.f_status.set(b.booking_status or "Pending")
                self.set_status(f"Selected: {b.booking_id}", "lightblue")
        except Exception:
            pass

    def get_form_data(self):
        return {
            "flight_id":      self.f_flight.get(),
            "passenger_id":   self.f_passenger.get(),
            "booking_date":   self.f_date.get().strip() or None,
            "seat_assignment": self.f_seat.get().strip(),
            "booking_status": self.f_status.get(),
        }

    def add_booking(self):
        try:
            b = Booking(booking_id=str(uuid.uuid4())[:8].upper(), **self.get_form_data())
            self.session.add(b)
            self.session.commit()
            self.load_bookings()
            self.clear_form()
            self.set_status("✅ Booking added!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def update_booking(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a booking first.", "orange"); return
        try:
            b = self.session.query(Booking).filter_by(booking_id=self.selected_id).first()
            for k, v in self.get_form_data().items():
                setattr(b, k, v)
            self.session.commit()
            self.load_bookings()
            self.set_status("✅ Updated!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def delete_booking(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a booking first.", "orange")
            return
        ok, msg = safe_delete(Booking, "booking_id", self.selected_id)
        if ok:
            self.selected_id = None
            self.session = __import__('database.connection', fromlist=['get_session']).get_session()
            self.load_bookings()
            self.clear_form()
            self.set_status("🗑 Deleted.", "gray")
        else:
            self.set_status(f"❌ {msg}", "red")

    def _clear_fields(self):
        for w in [self.f_date, self.f_seat]:
            w.delete(0, "end")
        self.f_status.set("Pending")

    def clear_form(self):
        self.selected_id = None
        self._clear_fields()
        self.set_status("", "gray")

    def set_status(self, msg, color="gray"):
        self.status_label.configure(text=msg, text_color=color)
