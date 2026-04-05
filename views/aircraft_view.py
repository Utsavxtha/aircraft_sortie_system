import customtkinter as ctk
from database.connection import get_session
from database.models import Aircraft
import uuid
from datetime import date
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


class AircraftView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = get_session()
        self.selected_id = None
        self.build_ui()
        self.load_aircraft()

    def build_ui(self):
        ctk.CTkLabel(self, text="✈  Aircraft Management", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        # Main layout
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=5)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        # ── LEFT: Form ──────────────────────────────────────────
        form_outer = ctk.CTkFrame(main)
        form_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(form_outer, text="Add / Edit Aircraft", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        form = ctk.CTkFrame(form_outer, fg_color="transparent")
        form.pack(padx=10, pady=5, fill="x")

        self.f_reg    = make_field(form, "Registration No.", 0)
        self.f_model  = make_field(form, "Model",            1)
        self.f_type   = make_field(form, "Type",             2, ["Fighter", "Transport", "Helicopter", "Trainer", "Bomber"])
        self.f_status = make_field(form, "Status",           3, ["Active", "Maintenance", "Retired", "Standby"])
        self.f_hours  = make_field(form, "Flight Hours Total", 4)
        self.f_maint  = make_field(form, "Last Maintenance (YYYY-MM-DD)", 5)

        # Buttons
        btn_frame = ctk.CTkFrame(form_outer, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="➕ Add",    width=90, command=self.add_aircraft).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Update", width=90, command=self.update_aircraft, fg_color="#2a7d4f").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑 Delete", width=90, command=self.delete_aircraft, fg_color="#a33").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Clear",  width=90, command=self.clear_form,      fg_color="gray").pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(form_outer, text="", font=("Arial", 11), text_color="gray")
        self.status_label.pack(pady=(0, 10))

        # ── RIGHT: List ─────────────────────────────────────────
        list_outer = ctk.CTkFrame(main)
        list_outer.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(list_outer, text="Aircraft List", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkButton(list_outer, text="🔄 Refresh", command=self.load_aircraft, width=100).pack(pady=(0, 5))

        self.listbox = ctk.CTkTextbox(list_outer, font=("Courier", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.listbox.bind("<ButtonRelease-1>", self.on_select)

    # ── Data helpers ─────────────────────────────────────────────

    def load_aircraft(self):
        self.aircraft_data = self.session.query(Aircraft).all()
        self.listbox.delete("1.0", "end")
        header = f"{'ID':<8}  {'Reg':<12}  {'Model':<18}  {'Type':<12}  {'Status':<12}  {'Hours'}\n"
        self.listbox.insert("end", header)
        self.listbox.insert("end", "-" * 75 + "\n")
        for a in self.aircraft_data:
            line = f"{a.aircraft_id:<8}  {a.registration_number:<12}  {a.model:<18}  {a.type:<12}  {a.status:<12}  {a.flight_hours_total}\n"
            self.listbox.insert("end", line)

    def on_select(self, event):
        try:
            index = int(self.listbox.index("insert").split(".")[0]) - 3
            if 0 <= index < len(self.aircraft_data):
                a = self.aircraft_data[index]
                self.selected_id = a.aircraft_id  
                self._clear_fields()              
                self.f_reg.insert(0, a.registration_number or "")
                self.f_model.insert(0, a.model or "")
                self.f_type.set(a.type or "Fighter")
                self.f_status.set(a.status or "Active")
                self.f_hours.insert(0, str(a.flight_hours_total or ""))
                self.f_maint.insert(0, str(a.last_maintenance_date or ""))
                self.set_status(f"Selected: {a.aircraft_id}", "lightblue")
        except Exception:
            pass

    def get_form_data(self):
        return {
            "registration_number": self.f_reg.get().strip(),
            "model":               self.f_model.get().strip(),
            "type":                self.f_type.get(),
            "status":              self.f_status.get(),
            "flight_hours_total":  self.f_hours.get().strip() or 0,
            "last_maintenance_date": self.f_maint.get().strip() or None,
        }

    def add_aircraft(self):
        try:
            d = self.get_form_data()
            a = Aircraft(aircraft_id=str(uuid.uuid4())[:8].upper(), **d)
            self.session.add(a)
            self.session.commit()
            self.load_aircraft()
            self.clear_form()
            self.set_status("✅ Aircraft added!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def update_aircraft(self):
        if not self.selected_id:
            self.set_status("⚠️ Select an aircraft first.", "orange")
            return
        try:
            a = self.session.query(Aircraft).filter_by(aircraft_id=self.selected_id).first()
            d = self.get_form_data()
            for k, v in d.items():
                setattr(a, k, v)
            self.session.commit()
            self.load_aircraft()
            self.set_status("✅ Updated!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def delete_aircraft(self):
        if not self.selected_id:
            self.set_status("⚠️ Select an aircraft first.", "orange")
            return
        ok, msg = safe_delete(Aircraft, "aircraft_id", self.selected_id)
        if ok:
            self.selected_id = None
            self.session = __import__('database.connection', fromlist=['get_session']).get_session()
            self.load_aircraft()
            self.clear_form()
            self.set_status("🗑 Deleted.", "gray")
        else:
            self.set_status(f"❌ {msg}", "red")

    def _clear_fields(self):
        """Clear input fields only, preserving selected_id."""
        for w in [self.f_reg, self.f_model, self.f_hours, self.f_maint]:
            w.delete(0, "end")
        self.f_type.set("Fighter")
        self.f_status.set("Active")
            
    def clear_form(self):
        """Full reset including selected_id — used by Clear button."""
        self.selected_id = None
        self._clear_fields()
        self.set_status("", "gray")

    def set_status(self, msg, color="gray"):
        self.status_label.configure(text=msg, text_color=color)
