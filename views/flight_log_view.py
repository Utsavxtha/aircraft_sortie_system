import customtkinter as ctk
from database.connection import get_session
from database.models import FlightLog, Flight
import uuid
from database.utils import safe_delete

LABEL_FONT = ("Arial", 12)
ENTRY_WIDTH = 280


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


class FlightLogView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = get_session()
        self.selected_id = None
        self.build_ui()
        self.load_logs()

    def build_ui(self):
        ctk.CTkLabel(self, text="📋  Flight Log", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=5)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        form_outer = ctk.CTkFrame(main)
        form_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(form_outer, text="Add / Edit Log Entry", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        form = ctk.CTkFrame(form_outer, fg_color="transparent")
        form.pack(padx=10, pady=5, fill="x")

        flight_ids = [f.flight_id for f in self.session.query(Flight).all()] or ["None"]

        self.f_flight = make_field(form, "Flight ID",                  0, flight_ids)
        self.f_time   = make_field(form, "Log Time (YYYY-MM-DD HH:MM:SS)", 1)
        self.f_type   = make_field(form, "Log Type",                   2, ["Departure", "Waypoint", "Arrival", "Emergency", "Fuel Check", "Weather"])
        self.f_desc   = make_field(form, "Description",                3)
        self.f_loc    = make_field(form, "Location",                   4)
        self.f_fuel   = make_field(form, "Fuel Remaining (L)",         5)

        btn_frame = ctk.CTkFrame(form_outer, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="➕ Add",    width=90, command=self.add_log).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Update", width=90, command=self.update_log, fg_color="#2a7d4f").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑 Delete", width=90, command=self.delete_log, fg_color="#a33").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Clear",  width=90, command=self.clear_form, fg_color="gray").pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(form_outer, text="", font=("Arial", 11), text_color="gray")
        self.status_label.pack(pady=(0, 10))

        list_outer = ctk.CTkFrame(main)
        list_outer.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(list_outer, text="Log Entries", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkButton(list_outer, text="🔄 Refresh", command=self.load_logs, width=100).pack(pady=(0, 5))
        self.listbox = ctk.CTkTextbox(list_outer, font=("Courier", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.listbox.bind("<ButtonRelease-1>", self.on_select)

    def load_logs(self):
        self.log_data = self.session.query(FlightLog).all()
        self.listbox.delete("1.0", "end")
        header = f"{'ID':<8}  {'Flight':<8}  {'Type':<12}  {'Time':<22}  {'Location'}\n"
        self.listbox.insert("end", header)
        self.listbox.insert("end", "-" * 70 + "\n")
        for l in self.log_data:
            self.listbox.insert("end", f"{l.log_id:<8}  {l.flight_id:<8}  {l.log_type:<12}  {str(l.log_time):<22}  {l.location}\n")

    def on_select(self, event):
        try:
            index = int(self.listbox.index("insert").split(".")[0]) - 3
            if 0 <= index < len(self.log_data):
                l = self.log_data[index]
                self.selected_id = l.log_id
                self._clear_fields()
                self.f_flight.set(l.flight_id)
                self.f_time.insert(0, str(l.log_time or ""))
                self.f_type.set(l.log_type or "Departure")
                self.f_desc.insert(0, l.description or "")
                self.f_loc.insert(0, l.location or "")
                self.f_fuel.insert(0, str(l.fuel_remaining or ""))
                self.set_status(f"Selected: {l.log_id}", "lightblue")
        except Exception:
            pass

    def get_form_data(self):
        return {
            "flight_id":      self.f_flight.get(),
            "log_time":       self.f_time.get().strip() or None,
            "log_type":       self.f_type.get(),
            "description":    self.f_desc.get().strip(),
            "location":       self.f_loc.get().strip(),
            "fuel_remaining": self.f_fuel.get().strip() or 0,
        }

    def add_log(self):
        try:
            l = FlightLog(log_id=str(uuid.uuid4())[:8].upper(), **self.get_form_data())
            self.session.add(l)
            self.session.commit()
            self.load_logs()
            self.clear_form()
            self.set_status("✅ Log added!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def update_log(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a log first.", "orange"); return
        try:
            l = self.session.query(FlightLog).filter_by(log_id=self.selected_id).first()
            for k, v in self.get_form_data().items():
                setattr(l, k, v)
            self.session.commit()
            self.load_logs()
            self.set_status("✅ Updated!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def delete_log(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a log first.", "orange")
            return
        ok, msg = safe_delete(FlightLog, "log_id", self.selected_id)
        if ok:
            self.selected_id = None
            self.session = __import__('database.connection', fromlist=['get_session']).get_session()
            self.load_logs()
            self.clear_form()
            self.set_status("🗑 Deleted.", "gray")
        else:
            self.set_status(f"❌ {msg}", "red")

    def _clear_fields(self):
        for w in [self.f_time, self.f_desc, self.f_loc, self.f_fuel]:
            w.delete(0, "end")
        self.f_type.set("Departure") 

    def clear_form(self):
        self.selected_id = None
        self._clear_fields()
        self.set_status("", "gray")

    def set_status(self, msg, color="gray"):
        self.status_label.configure(text=msg, text_color=color)
