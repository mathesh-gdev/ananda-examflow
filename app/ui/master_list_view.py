"""
master_list_view.py — The searchable master allotment table.

Displays every allocated student in a scrollable table with columns:
  S.No | Register Number | Academic Year | Hall | Seat Location

Supports:
  - Real-time text search (filters by roll number or hall name)
  - Year dropdown filter (All / 1st / 2nd / 3rd Year)

Replaces the "Master Allotment List" tab from admin.html.
"""

import customtkinter as ctk

from app.constants import YEARS


class MasterListView(ctk.CTkFrame):
    """
    A frame containing a search bar and a scrollable table of student records.

    Usage:
        view = MasterListView(parent)
        view.load_data(master_records)   # populate the table
        view.clear()                      # reset to empty
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._all_records = []   # Full unfiltered dataset
        self._row_widgets = []   # References to table row frames

        # ---- Search Controls ----
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(fill="x", padx=5, pady=(5, 10))

        # Search input
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._apply_filter())

        search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Search by roll number or hall...",
            textvariable=self._search_var,
            width=300,
            height=35,
            font=ctk.CTkFont(size=13),
        )
        search_entry.pack(side="left", padx=(0, 10))

        # Year filter dropdown
        self._year_var = ctk.StringVar(value="All Years")
        year_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["All Years", "1st Year", "2nd Year", "3rd Year"],
            variable=self._year_var,
            width=140,
            height=35,
            command=lambda _: self._apply_filter(),
        )
        year_menu.pack(side="left")

        # ---- Table Header Row ----
        header_frame = ctk.CTkFrame(self, fg_color=("gray90", "#1e293b"), corner_radius=6)
        header_frame.pack(fill="x", padx=5, pady=(0, 2))

        headers = [
            ("S.No", 50),
            ("Register Number", 160),
            ("Academic Year", 140),
            ("Hall", 80),
            ("Seat Location", 280),
        ]
        for text, width in headers:
            ctk.CTkLabel(
                header_frame,
                text=text,
                width=width,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("gray30", "gray70"),
                anchor="w",
            ).pack(side="left", padx=6, pady=6)

        # ---- Scrollable Table Body ----
        self._table_body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self._table_body.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Empty state placeholder
        self._empty_label = ctk.CTkLabel(
            self._table_body,
            text="No seating records to display.\nGenerate an allotment first.",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60"),
        )
        self._empty_label.pack(pady=40)

    def load_data(self, records: list[dict]):
        """
        Populate the table with master list records.

        Parameters
        ----------
        records : list of dicts with keys: roll, year, hall, location
        """
        self._all_records = records
        self._rebuild_table(records)

    def clear(self):
        """Reset the table to the empty state."""
        self._all_records = []
        self._clear_table()
        self._empty_label = ctk.CTkLabel(
            self._table_body,
            text="No seating records to display.\nGenerate an allotment first.",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60"),
        )
        self._empty_label.pack(pady=40)

    def _clear_table(self):
        """Remove all row widgets from the table body."""
        for widget in self._table_body.winfo_children():
            widget.destroy()
        self._row_widgets = []

    def _rebuild_table(self, records: list[dict]):
        """Recreate the entire table with the given records."""
        self._clear_table()

        if not records:
            self._empty_label = ctk.CTkLabel(
                self._table_body,
                text="No matching records found.",
                font=ctk.CTkFont(size=13),
                text_color=("gray50", "gray60"),
            )
            self._empty_label.pack(pady=40)
            return

        for i, record in enumerate(records, start=1):
            # Alternate row backgrounds for readability.
            bg = ("gray97", "#12182d") if i % 2 == 0 else ("white", "#161d35")

            row_frame = ctk.CTkFrame(
                self._table_body,
                fg_color=bg,
                corner_radius=4,
                height=32,
            )
            row_frame.pack(fill="x", pady=1)

            year_info = YEARS.get(record["year"], {})
            year_label = year_info.get("label", f"Year {record['year']}")

            # Pick a text color for the year badge based on year number.
            year_color = {
                1: "#3b82f6", 2: "#10b981", 3: "#f59e0b",
                4: "#3b82f6", 5: "#10b981",
            }.get(record["year"], "gray50")

            # S.No
            ctk.CTkLabel(
                row_frame, text=str(i), width=50,
                font=ctk.CTkFont(size=11),
                text_color=("gray40", "gray60"),
                anchor="w",
            ).pack(side="left", padx=6, pady=4)

            # Register Number
            ctk.CTkLabel(
                row_frame, text=record["roll"], width=160,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("gray10", "gray90"),
                anchor="w",
            ).pack(side="left", padx=6, pady=4)

            # Academic Year
            ctk.CTkLabel(
                row_frame, text=year_label, width=140,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=year_color,
                anchor="w",
            ).pack(side="left", padx=6, pady=4)

            # Hall
            ctk.CTkLabel(
                row_frame, text=record["hall"], width=80,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#4f46e5", "#818cf8"),
                anchor="w",
            ).pack(side="left", padx=6, pady=4)

            # Seat Location
            ctk.CTkLabel(
                row_frame, text=record["location"], width=280,
                font=ctk.CTkFont(size=10),
                text_color=("gray40", "gray60"),
                anchor="w",
            ).pack(side="left", padx=6, pady=4)

            self._row_widgets.append(row_frame)

    def _apply_filter(self):
        """Filter the table based on the search text and year dropdown."""
        query = self._search_var.get().lower().strip()
        year_filter = self._year_var.get()

        # Map dropdown text to year numbers.
        year_map = {
            "1st Year": [1, 4],
            "2nd Year": [2, 5],
            "3rd Year": [3],
        }
        allowed_years = year_map.get(year_filter, None)  # None = all years

        filtered = []
        for record in self._all_records:
            # Check year filter.
            if allowed_years and record["year"] not in allowed_years:
                continue
            # Check text search.
            if query:
                if query not in record["roll"].lower() and \
                   query not in record["hall"].lower():
                    continue
            filtered.append(record)

        self._rebuild_table(filtered)
