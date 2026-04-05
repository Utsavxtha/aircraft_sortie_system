import customtkinter as ctk
from database.connection import get_session
from database.models import Passenger
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


class PassengerView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = get_session()
        self.selected_id = None
        self.build_ui()
        self.load_passengers()

    def build_ui(self):
        ctk.CTkLabel(self, text="🧳  Passenger Management", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=5)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        form_outer = ctk.CTkFrame(main)
        form_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(form_outer, text="Add / Edit Passenger", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        form = ctk.CTkFrame(form_outer, fg_color="transparent")
        form.pack(padx=10, pady=5, fill="x")

        self.f_ticket   = make_field(form, "Ticket Number",  0)
        self.f_first    = make_field(form, "First Name",     1)
        self.f_last     = make_field(form, "Last Name",      2)
        self.f_class    = make_field(form, "Class",          3, ["Economy", "Business", "First Class"])
        self.f_status   = make_field(form, "Status",         4, ["Active", "Inactive", "Boarded", "No Show"])
        self.f_passport = make_field(form, "Passport Number",5)

        btn_frame = ctk.CTkFrame(form_outer, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="➕ Add",    width=90, command=self.add_passenger).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Update", width=90, command=self.update_passenger, fg_color="#2a7d4f").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑 Delete", width=90, command=self.delete_passenger, fg_color="#a33").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Clear",  width=90, command=self.clear_form,       fg_color="gray").pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(form_outer, text="", font=("Arial", 11), text_color="gray")
        self.status_label.pack(pady=(0, 10))

        list_outer = ctk.CTkFrame(main)
        list_outer.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(list_outer, text="Passenger List", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkButton(list_outer, text="🔄 Refresh", command=self.load_passengers, width=100).pack(pady=(0, 5))
        self.listbox = ctk.CTkTextbox(list_outer, font=("Courier", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.listbox.bind("<ButtonRelease-1>", self.on_select)

    def load_passengers(self):
        self.passenger_data = self.session.query(Passenger).all()
        self.listbox.delete("1.0", "end")
        header = f"{'ID':<8}  {'Ticket':<10}  {'Name':<22}  {'Class':<14}  {'Status'}\n"
        self.listbox.insert("end", header)
        self.listbox.insert("end", "-" * 70 + "\n")
        for p in self.passenger_data:
            self.listbox.insert("end", f"{p.passenger_id:<8}  {p.ticket_number:<10}  {(p.first_name+' '+p.last_name):<22}  {p.class_:<14}  {p.status}\n")

    def on_select(self, event):
        try:
            index = int(self.listbox.index("insert").split(".")[0]) - 3
            if 0 <= index < len(self.passenger_data):
                p = self.passenger_data[index]
                self.selected_id = p.passenger_id
                self._clear_fields()
                self.f_ticket.insert(0, p.ticket_number or "")
                self.f_first.insert(0, p.first_name or "")
                self.f_last.insert(0, p.last_name or "")
                self.f_class.set(p.class_ or "Economy")
                self.f_status.set(p.status or "Active")
                self.f_passport.insert(0, p.passport_number or "")
                self.set_status(f"Selected: {p.passenger_id}", "lightblue")
        except Exception:
            pass

    def get_form_data(self):
        return {
            "ticket_number":   self.f_ticket.get().strip(),
            "first_name":      self.f_first.get().strip(),
            "last_name":       self.f_last.get().strip(),
            "class_":          self.f_class.get(),
            "status":          self.f_status.get(),
            "passport_number": self.f_passport.get().strip(),
        }

    def add_passenger(self):
        try:
            p = Passenger(passenger_id=str(uuid.uuid4())[:8].upper(), **self.get_form_data())
            self.session.add(p)
            self.session.commit()
            self.load_passengers()
            self.clear_form()
            self.set_status("✅ Passenger added!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def update_passenger(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a passenger first.", "orange"); return
        try:
            p = self.session.query(Passenger).filter_by(passenger_id=self.selected_id).first()
            for k, v in self.get_form_data().items():
                setattr(p, k, v)
            self.session.commit()
            self.load_passengers()
            self.set_status("✅ Updated!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def delete_passenger(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a passenger first.", "orange")
            return
        ok, msg = safe_delete(Passenger, "passenger_id", self.selected_id)
        if ok:
            self.selected_id = None
            self.session = __import__('database.connection', fromlist=['get_session']).get_session()
            self.load_passengers()
            self.clear_form()
            self.set_status("🗑 Deleted.", "gray")
        else:
            self.set_status(f"❌ {msg}", "red")

    def _clear_fields(self):
        for w in [self.f_ticket, self.f_first, self.f_last, self.f_passport]:
            w.delete(0, "end")
        self.f_class.set("Economy")
        self.f_status.set("Active")

    def clear_form(self):
        self.selected_id = None
        self._clear_fields()
        self.set_status("", "gray")

    def set_status(self, msg, color="gray"):
        self.status_label.configure(text=msg, text_color=color)
