import customtkinter as ctk
from database.connection import get_session
from database.models import Crew, Flight, Pilot
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


class CrewView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = get_session()
        self.selected_id = None
        self.build_ui()
        self.load_crew()

    def build_ui(self):
        ctk.CTkLabel(self, text="👥  Crew Management", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=5)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        form_outer = ctk.CTkFrame(main)
        form_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(form_outer, text="Add / Edit Crew", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        form = ctk.CTkFrame(form_outer, fg_color="transparent")
        form.pack(padx=10, pady=5, fill="x")

        flight_ids = [f.flight_id for f in self.session.query(Flight).all()] or ["None"]
        pilot_ids  = [p.pilot_id  for p in self.session.query(Pilot).all()]  or ["None"]

        self.f_flight = make_field(form, "Flight ID",     0, flight_ids)
        self.f_pilot  = make_field(form, "Pilot ID",      1, pilot_ids)
        self.f_role   = make_field(form, "Role",          2, ["Pilot in Command", "Co-Pilot", "Flight Engineer", "Navigator", "Loadmaster"])
        self.f_duty   = make_field(form, "Duty Station",  3, ["Cockpit", "Cabin", "Rear", "Observer"])

        btn_frame = ctk.CTkFrame(form_outer, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="➕ Add",    width=90, command=self.add_crew).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Update", width=90, command=self.update_crew, fg_color="#2a7d4f").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑 Delete", width=90, command=self.delete_crew, fg_color="#a33").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Clear",  width=90, command=self.clear_form,  fg_color="gray").pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(form_outer, text="", font=("Arial", 11), text_color="gray")
        self.status_label.pack(pady=(0, 10))

        list_outer = ctk.CTkFrame(main)
        list_outer.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(list_outer, text="Crew List", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkButton(list_outer, text="🔄 Refresh", command=self.load_crew, width=100).pack(pady=(0, 5))
        self.listbox = ctk.CTkTextbox(list_outer, font=("Courier", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.listbox.bind("<ButtonRelease-1>", self.on_select)

    def load_crew(self):
        self.crew_data = self.session.query(Crew).all()
        self.listbox.delete("1.0", "end")
        header = f"{'ID':<8}  {'Flight':<8}  {'Pilot':<8}  {'Role':<22}  {'Duty Station'}\n"
        self.listbox.insert("end", header)
        self.listbox.insert("end", "-" * 70 + "\n")
        for c in self.crew_data:
            self.listbox.insert("end", f"{c.crew_id:<8}  {c.flight_id:<8}  {c.pilot_id:<8}  {c.role:<22}  {c.duty_station}\n")

    def on_select(self, event):
        try:
            index = int(self.listbox.index("insert").split(".")[0]) - 3
            if 0 <= index < len(self.crew_data):
                c = self.crew_data[index]
                self.selected_id = c.crew_id
                self.f_flight.set(c.flight_id)
                self.f_pilot.set(c.pilot_id)
                self.f_role.set(c.role)
                self.f_duty.set(c.duty_station)
                self.set_status(f"Selected: {c.crew_id}", "lightblue")
        except Exception:
            pass

    def get_form_data(self):
        return {
            "flight_id":    self.f_flight.get(),
            "pilot_id":     self.f_pilot.get(),
            "role":         self.f_role.get(),
            "duty_station": self.f_duty.get(),
        }

    def add_crew(self):
        try:
            c = Crew(crew_id=str(uuid.uuid4())[:8].upper(), **self.get_form_data())
            self.session.add(c)
            self.session.commit()
            self.load_crew()
            self.clear_form()
            self.set_status("✅ Crew added!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def update_crew(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a crew first.", "orange"); return
        try:
            c = self.session.query(Crew).filter_by(crew_id=self.selected_id).first()
            for k, v in self.get_form_data().items():
                setattr(c, k, v)
            self.session.commit()
            self.load_crew()
            self.set_status("✅ Updated!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def delete_crew(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a crew first.", "orange")
            return
        ok, msg = safe_delete(Crew, "crew_id", self.selected_id)
        if ok:
            self.selected_id = None
            self.session = __import__('database.connection', fromlist=['get_session']).get_session()
            self.load_crew()
            self.clear_form()
            self.set_status("🗑 Deleted.", "gray")
        else:
            self.set_status(f"❌ {msg}", "red")

    def clear_form(self):
        self.selected_id = None
        self.f_role.set("Pilot in Command")
        self.f_duty.set("Cockpit")
        self.set_status("", "gray")

    def set_status(self, msg, color="gray"):
        self.status_label.configure(text=msg, text_color=color)
