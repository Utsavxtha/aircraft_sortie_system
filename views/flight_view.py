import customtkinter as ctk
from database.connection import get_session
from database.models import Flight, Aircraft
import uuid
from database.utils import safe_delete

LABEL_FONT = ("Arial", 12)
ENTRY_WIDTH = 280


def make_field(parent, label, row, values=None):
    ctk.CTkLabel(parent, text=label, font=LABEL_FONT, anchor="w").grid(
        row=row, column=0, sticky="w", padx=(10, 5), pady=4
    )
    if values:
        widget = ctk.CTkOptionMenu(parent, values=values, width=ENTRY_WIDTH)
    else:
        widget = ctk.CTkEntry(parent, width=ENTRY_WIDTH)
    widget.grid(row=row, column=1, sticky="w", padx=(0, 10), pady=4)
    return widget


class FlightView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = get_session()
        self.selected_id = None
        self.build_ui()
        self.load_flights()

    def build_ui(self):
        ctk.CTkLabel(self, text="🛫  Flight Management", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=5)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        # ── LEFT: Form ──────────────────────────────────────────
        form_outer = ctk.CTkScrollableFrame(main, width=380)
        form_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(form_outer, text="Add / Edit Flight", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 5)
        )

        aircraft_ids = [a.aircraft_id for a in self.session.query(Aircraft).all()] or ["None"]

        self.f_number  = make_field(form_outer, "Flight Number",        1)
        self.f_call    = make_field(form_outer, "Call Sign",             2)
        self.f_acft    = make_field(form_outer, "Aircraft ID",           3, aircraft_ids)
        self.f_date    = make_field(form_outer, "Flight Date (YYYY-MM-DD)", 4)
        self.f_edep    = make_field(form_outer, "Est. Departure (HH:MM:SS)", 5)
        self.f_earr    = make_field(form_outer, "Est. Arrival (HH:MM:SS)",   6)
        self.f_adep    = make_field(form_outer, "Act. Departure (HH:MM:SS)", 7)
        self.f_aarr    = make_field(form_outer, "Act. Arrival (HH:MM:SS)",   8)
        self.f_purpose = make_field(form_outer, "Flight Purpose",        9)
        self.f_plan    = make_field(form_outer, "Flight Plan",           10)
        self.f_status  = make_field(form_outer, "Status",               11, ["Scheduled", "In Progress", "Completed", "Cancelled", "Delayed"])
        self.f_dur     = make_field(form_outer, "Duration (hrs)",        12)
        self.f_mission = make_field(form_outer, "Mission Type",         13, ["Training", "Combat", "Logistics", "Reconnaissance", "Search & Rescue"])

        btn_frame = ctk.CTkFrame(form_outer, fg_color="transparent")
        btn_frame.grid(row=14, column=0, columnspan=2, pady=10)

        ctk.CTkButton(btn_frame, text="➕ Add",    width=90, command=self.add_flight).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Update", width=90, command=self.update_flight, fg_color="#2a7d4f").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑 Delete", width=90, command=self.delete_flight, fg_color="#a33").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Clear",  width=90, command=self.clear_form,    fg_color="gray").pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(form_outer, text="", font=("Arial", 11), text_color="gray")
        self.status_label.grid(row=15, column=0, columnspan=2, pady=(0, 10))

        # ── RIGHT: List ─────────────────────────────────────────
        list_outer = ctk.CTkFrame(main)
        list_outer.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(list_outer, text="Flight List", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkButton(list_outer, text="🔄 Refresh", command=self.load_flights, width=100).pack(pady=(0, 5))

        self.listbox = ctk.CTkTextbox(list_outer, font=("Courier", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.listbox.bind("<ButtonRelease-1>", self.on_select)

    def load_flights(self):
        self.flight_data = self.session.query(Flight).all()
        self.listbox.delete("1.0", "end")
        header = f"{'ID':<8}  {'Number':<14}  {'Call':<8}  {'Date':<12}  {'Status':<12}  {'Mission'}\n"
        self.listbox.insert("end", header)
        self.listbox.insert("end", "-" * 80 + "\n")
        for f in self.flight_data:
            line = f"{f.flight_id:<8}  {f.flight_number:<14}  {f.call_sign:<8}  {str(f.flight_date):<12}  {f.status:<12}  {f.mission_type}\n"
            self.listbox.insert("end", line)

    def on_select(self, event):
        try:
            index = int(self.listbox.index("insert").split(".")[0]) - 3
            if 0 <= index < len(self.flight_data):
                f = self.flight_data[index]
                self.selected_id = f.flight_id
                self._clear_fields()
                self.f_number.insert(0, f.flight_number or "")
                self.f_call.insert(0, f.call_sign or "")
                self.f_acft.set(f.aircraft_id or "")
                self.f_date.insert(0, str(f.flight_date or ""))
                self.f_edep.insert(0, str(f.estimated_departure or ""))
                self.f_earr.insert(0, str(f.estimated_arrival or ""))
                self.f_adep.insert(0, str(f.actual_departure or ""))
                self.f_aarr.insert(0, str(f.actual_arrival or ""))
                self.f_purpose.insert(0, f.flight_purpose or "")
                self.f_plan.insert(0, f.flight_plan or "")
                self.f_status.set(f.status or "Scheduled")
                self.f_dur.insert(0, str(f.flight_duration or ""))
                self.f_mission.set(f.mission_type or "Training")
                self.set_status(f"Selected: {f.flight_id}", "lightblue")
        except Exception:
            pass

    def get_form_data(self):
        return {
            "flight_number":       self.f_number.get().strip(),
            "call_sign":           self.f_call.get().strip(),
            "aircraft_id":         self.f_acft.get(),
            "flight_date":         self.f_date.get().strip() or None,
            "estimated_departure": self.f_edep.get().strip() or None,
            "estimated_arrival":   self.f_earr.get().strip() or None,
            "actual_departure":    self.f_adep.get().strip() or None,
            "actual_arrival":      self.f_aarr.get().strip() or None,
            "flight_purpose":      self.f_purpose.get().strip(),
            "flight_plan":         self.f_plan.get().strip(),
            "status":              self.f_status.get(),
            "flight_duration":     self.f_dur.get().strip() or 0,
            "mission_type":        self.f_mission.get(),
        }

    def add_flight(self):
        try:
            d = self.get_form_data()
            f = Flight(flight_id=str(uuid.uuid4())[:8].upper(), **d)
            self.session.add(f)
            self.session.commit()
            self.load_flights()
            self.clear_form()
            self.set_status("✅ Flight added!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def update_flight(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a flight first.", "orange")
            return
        try:
            f = self.session.query(Flight).filter_by(flight_id=self.selected_id).first()
            for k, v in self.get_form_data().items():
                setattr(f, k, v)
            self.session.commit()
            self.load_flights()
            self.set_status("✅ Updated!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def delete_flight(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a flight first.", "orange")
            return
        ok, msg = safe_delete(Flight, "flight_id", self.selected_id)
        if ok:
            self.selected_id = None
            self.session = __import__('database.connection', fromlist=['get_session']).get_session()
            self.load_flights()
            self.clear_form()
            self.set_status("🗑 Deleted.", "gray")
        else:
            self.set_status(f"❌ {msg}", "red")

    def _clear_fields(self):
        for w in [self.f_number, self.f_call, self.f_date, self.f_edep,
                  self.f_earr, self.f_adep, self.f_aarr, self.f_purpose,
                  self.f_plan, self.f_dur]:
            w.delete(0, "end")
        self.f_status.set("Scheduled")
        self.f_mission.set("Training")

    def clear_form(self):
        self.selected_id = None
        self._clear_fields()
        self.set_status("", "gray")

    def set_status(self, msg, color="gray"):
        self.status_label.configure(text=msg, text_color=color)
