import customtkinter as ctk
from database.connection import get_session
from sqlalchemy import text
from database.utils import safe_delete

class QueryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = get_session()
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="SQL Query Console", font=("Arial", 20, "bold")).pack(pady=10)

        # Query input box
        ctk.CTkLabel(self, text="Enter SQL Query:").pack(anchor="w", padx=15)
        self.query_input = ctk.CTkTextbox(self, height=120, font=("Courier", 13))
        self.query_input.pack(fill="x", padx=15, pady=5)
        self.query_input.insert("1.0", "SELECT * FROM aircraft;")

        # Buttons row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(btn_frame, text="▶  Run Query", command=self.run_query).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑  Clear", command=self.clear_all, fg_color="gray").pack(side="left", padx=5)

        # Quick query buttons
        ctk.CTkLabel(self, text="Quick Queries:").pack(anchor="w", padx=15, pady=(10, 2))
        quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_frame.pack(fill="x", padx=15, pady=2)

        quick_queries = [
            ("All Aircraft",     "SELECT * FROM aircraft;"),
            ("All Pilots",       "SELECT * FROM pilot;"),
            ("All Flights",      "SELECT * FROM flight;"),
            ("All Crew",         "SELECT * FROM crew;"),
            ("All Logs",         "SELECT * FROM flight_log;"),
            ("All Bookings",     "SELECT * FROM booking;"),
            ("All Passengers",   "SELECT * FROM passenger;"),
            ("Active Aircraft",  "SELECT * FROM aircraft WHERE status = 'Active';"),
            ("Active Pilots",    "SELECT * FROM pilot WHERE status = 'Active';"),
            ("Scheduled Flights","SELECT * FROM flight WHERE status = 'Scheduled';"),
            ("Flights + Aircraft",
             "SELECT f.flight_number, f.call_sign, a.model, a.registration_number, f.status\nFROM flight f JOIN aircraft a ON f.aircraft_id = a.aircraft_id;"),
            ("Crew + Pilot Names",
             "SELECT c.crew_id, f.flight_number, p.first_name, p.last_name, c.role\nFROM crew c\nJOIN pilot p ON c.pilot_id = p.pilot_id\nJOIN flight f ON c.flight_id = f.flight_id;"),
        ]

        for label, query in quick_queries:
            ctk.CTkButton(
                quick_frame, text=label, width=130, height=28,
                font=("Arial", 11),
                command=lambda q=query: self.load_quick(q)
            ).pack(side="left", padx=3, pady=2)

        # Row count label
        self.row_count_label = ctk.CTkLabel(self, text="", font=("Arial", 11), text_color="gray")
        self.row_count_label.pack(anchor="w", padx=15)

        # Results output
        ctk.CTkLabel(self, text="Results:").pack(anchor="w", padx=15, pady=(5, 2))
        self.results_box = ctk.CTkTextbox(self, font=("Courier", 12))
        self.results_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def load_quick(self, query):
        self.query_input.delete("1.0", "end")
        self.query_input.insert("1.0", query)
        self.run_query()

    def run_query(self):
        query = self.query_input.get("1.0", "end").strip()
        if not query:
            return

        self.results_box.delete("1.0", "end")

        try:
            result = self.session.execute(text(query))

            # Only fetch results for SELECT queries
            if query.strip().upper().startswith("SELECT"):
                rows = result.fetchall()
                columns = list(result.keys())

                if not rows:
                    self.results_box.insert("end", "No results found.")
                    self.row_count_label.configure(text="0 rows returned")
                    return

                # Calculate column widths
                col_widths = [len(c) for c in columns]
                for row in rows:
                    for i, val in enumerate(row):
                        col_widths[i] = max(col_widths[i], len(str(val)))

                # Build header
                header = "  ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(columns))
                separator = "  ".join("-" * col_widths[i] for i in range(len(columns)))

                self.results_box.insert("end", header + "\n")
                self.results_box.insert("end", separator + "\n")

                for row in rows:
                    line = "  ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
                    self.results_box.insert("end", line + "\n")

                self.row_count_label.configure(text=f"{len(rows)} row(s) returned")

            else:
                # For INSERT, UPDATE, DELETE
                self.session.commit()
                self.results_box.insert("end", "✅ Query executed successfully.")
                self.row_count_label.configure(text="")

        except Exception as e:
            self.session.rollback()
            self.results_box.insert("end", f"❌ Error:\n{str(e)}")
            self.row_count_label.configure(text="")

    def clear_all(self):
        self.query_input.delete("1.0", "end")
        self.results_box.delete("1.0", "end")
        self.row_count_label.configure(text="")