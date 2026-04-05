import customtkinter as ctk
from database.connection import get_session
from database.models import Pilot
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


class PilotView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = get_session()
        self.selected_id = None
        self.build_ui()
        self.load_pilots()

    def build_ui(self):
        ctk.CTkLabel(self, text="👨‍✈️  Pilot Management", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=5)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        # ── LEFT: Form ──────────────────────────────────────────
        form_outer = ctk.CTkFrame(main)
        form_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(form_outer, text="Add / Edit Pilot", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        form = ctk.CTkFrame(form_outer, fg_color="transparent")
        form.pack(padx=10, pady=5, fill="x")

        self.f_badge  = make_field(form, "Badge Number",       0)
        self.f_first  = make_field(form, "First Name",         1)
        self.f_last   = make_field(form, "Last Name",          2)
        self.f_rank   = make_field(form, "Rank",               3, ["Cadet", "Flight Lieutenant", "Squadron Leader", "Wing Commander", "Group Captain"])
        self.f_qual   = make_field(form, "Qualification Level",4, ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"])
        self.f_status = make_field(form, "Status",             5, ["Active", "Inactive", "On Leave", "Retired"])
        self.f_month  = make_field(form, "Flight Hours (Month)",6)
        self.f_total  = make_field(form, "Flight Hours (Total)",7)

        btn_frame = ctk.CTkFrame(form_outer, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="➕ Add",    width=90, command=self.add_pilot).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Update", width=90, command=self.update_pilot, fg_color="#2a7d4f").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑 Delete", width=90, command=self.delete_pilot, fg_color="#a33").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Clear",  width=90, command=self.clear_form,   fg_color="gray").pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(form_outer, text="", font=("Arial", 11), text_color="gray")
        self.status_label.pack(pady=(0, 10))

        # ── RIGHT: List ─────────────────────────────────────────
        list_outer = ctk.CTkFrame(main)
        list_outer.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(list_outer, text="Pilot List", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkButton(list_outer, text="🔄 Refresh", command=self.load_pilots, width=100).pack(pady=(0, 5))

        self.listbox = ctk.CTkTextbox(list_outer, font=("Courier", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.listbox.bind("<ButtonRelease-1>", self.on_select)

    def load_pilots(self):
        self.pilot_data = self.session.query(Pilot).all()
        self.listbox.delete("1.0", "end")
        header = f"{'ID':<8}  {'Badge':<8}  {'Name':<22}  {'Rank':<20}  {'Status'}\n"
        self.listbox.insert("end", header)
        self.listbox.insert("end", "-" * 75 + "\n")
        for p in self.pilot_data:
            line = f"{p.pilot_id:<8}  {p.badge_number:<8}  {(p.first_name+' '+p.last_name):<22}  {p.rank:<20}  {p.status}\n"
            self.listbox.insert("end", line)

    def on_select(self, event):
        try:
            index = int(self.listbox.index("insert").split(".")[0]) - 3
            if 0 <= index < len(self.pilot_data):
                p = self.pilot_data[index]
                self.selected_id = p.pilot_id
                self._clear_fields()
                self.f_badge.insert(0, p.badge_number or "")
                self.f_first.insert(0, p.first_name or "")
                self.f_last.insert(0, p.last_name or "")
                self.f_rank.set(p.rank or "Flight Lieutenant")
                self.f_qual.set(p.qualification_level or "Level 1")
                self.f_status.set(p.status or "Active")
                self.f_month.insert(0, str(p.flight_hours_month or ""))
                self.f_total.insert(0, str(p.flight_hours_total or ""))
                self.set_status(f"Selected: {p.pilot_id}", "lightblue")
        except Exception:
            pass

    def get_form_data(self):
        return {
            "badge_number":       self.f_badge.get().strip(),
            "first_name":         self.f_first.get().strip(),
            "last_name":          self.f_last.get().strip(),
            "rank":               self.f_rank.get(),
            "qualification_level":self.f_qual.get(),
            "status":             self.f_status.get(),
            "flight_hours_month": self.f_month.get().strip() or 0,
            "flight_hours_total": self.f_total.get().strip() or 0,
        }

    def add_pilot(self):
        try:
            d = self.get_form_data()
            p = Pilot(pilot_id=str(uuid.uuid4())[:8].upper(), **d)
            self.session.add(p)
            self.session.commit()
            self.load_pilots()
            self.clear_form()
            self.set_status("✅ Pilot added!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def update_pilot(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a pilot first.", "orange")
            return
        try:
            p = self.session.query(Pilot).filter_by(pilot_id=self.selected_id).first()
            for k, v in self.get_form_data().items():
                setattr(p, k, v)
            self.session.commit()
            self.load_pilots()
            self.set_status("✅ Updated!", "#2a7d4f")
        except Exception as e:
            self.session.rollback()
            self.set_status(f"❌ {e}", "red")

    def delete_pilot(self):
        if not self.selected_id:
            self.set_status("⚠️ Select a pilot first.", "orange")
            return
        ok, msg = safe_delete(Pilot, "pilot_id", self.selected_id)
        if ok:
            self.selected_id = None
            self.session = __import__('database.connection', fromlist=['get_session']).get_session()
            self.load_pilots()
            self.clear_form()
            self.set_status("🗑 Deleted.", "gray")
        else:
            self.set_status(f"❌ {msg}", "red")

    def _clear_fields(self):
        for w in [self.f_badge, self.f_first, self.f_last, self.f_month, self.f_total]:
            w.delete(0, "end")
        self.f_rank.set("Flight Lieutenant")
        self.f_qual.set("Level 1")
        self.f_status.set("Active")
 

    def clear_form(self):
        self.selected_id = None
        self._clear_fields()
        self.set_status("", "gray")

    def set_status(self, msg, color="gray"):
        self.status_label.configure(text=msg, text_color=color)
