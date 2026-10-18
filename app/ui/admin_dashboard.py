"""
admin_dashboard.py — Main administration workspace.

Orchestrates:
  - Left Sidebar: College headers, student group cards, hall configuration, action triggers
  - Right Content Area:
      - Tab 1: Dashboard & Live Classroom Seating Visualizer
      - Tab 2: Searchable Master Notice-Board Allotment Table
      - Tab 3: Operational Instructions & Architecture Guide
"""

import re
import customtkinter as ctk
from typing import List, Dict, Any, Optional

from app.constants import YEARS, DEGREES, DEFAULT_HALLS, DEFAULT_GROUPS
from app.allotment_engine import allocate_seating, parse_student_groups, build_master_list
from app.data_manager import DataManager
from app.export_service import ExportService, EXPORT_OPTIONS
from app.ui.group_card import GroupCard
from app.ui.hall_visualizer import HallVisualizer
from app.ui.master_list_view import MasterListView
from app.ui.toast_notification import show_toast


class AdminDashboard(ctk.CTkFrame):
    """
    Main admin interface connecting user inputs, allotment algorithms, and visual representations.
    """

    def __init__(self, parent, data_manager: DataManager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.dm = data_manager

        # Application State
        self.halls: List[Dict[str, Any]] = []
        self.group_cards: List[GroupCard] = []
        self.configured_halls: Dict[str, List[str]] = {"A": [], "B": [], "C": []}

        # 2-Column Responsive Layout: Fixed Sidebar (Left) + Expanding Content (Right)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()
        self._load_saved_data()

    # =========================================================================
    #  SIDEBAR LAYOUT
    # =========================================================================

    def _build_sidebar(self) -> None:
        """Constructs the scrollable left sidebar containing all configuration panels."""
        sidebar = ctk.CTkScrollableFrame(
            self,
            width=340,
            fg_color=("gray98", "#0f1525"),
            corner_radius=0,
        )
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 5))

        self._build_institution_section(sidebar)
        self._build_student_groups_section(sidebar)
        self._build_hall_settings_section(sidebar)
        self._build_action_buttons(sidebar)

    def _build_institution_section(self, parent) -> None:
        """Section 1: College Name and Examination Title."""
        card = ctk.CTkFrame(parent, fg_color=("white", "#161d35"), corner_radius=10)
        card.pack(fill="x", padx=8, pady=(8, 5))

        ctk.CTkLabel(
            card, text="🎓  College & Exam Header",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 5))

        # College Name Entry
        ctk.CTkLabel(
            card, text="COLLEGE NAME", font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60"), anchor="w",
        ).pack(fill="x", padx=12, pady=(4, 0))
        self.college_name_entry = ctk.CTkEntry(card, height=32, font=ctk.CTkFont(size=12))
        self.college_name_entry.pack(fill="x", padx=12, pady=(2, 5))
        self.college_name_entry.insert(0, "ANANDA COLLEGE OF ARTS & SCIENCE")

        # Exam Title Entry
        ctk.CTkLabel(
            card, text="EXAM / SESSION TITLE", font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60"), anchor="w",
        ).pack(fill="x", padx=12, pady=(4, 0))
        self.exam_title_entry = ctk.CTkEntry(card, height=32, font=ctk.CTkFont(size=12))
        self.exam_title_entry.pack(fill="x", padx=12, pady=(2, 10))
        self.exam_title_entry.insert(0, "Semester End Examinations - April 2026")

    def _build_student_groups_section(self, parent) -> None:
        """Section 2: Student Group configuration cards."""
        card = ctk.CTkFrame(parent, fg_color=("white", "#161d35"), corner_radius=10)
        card.pack(fill="x", padx=8, pady=5)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 5))

        ctk.CTkLabel(
            header, text="👥  Student Roll Numbers",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(side="left")

        # Add new group button
        add_btn = ctk.CTkButton(
            header, text="+", width=28, height=28,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#e0e7ff", "#2a2f55"),
            text_color=("#4f46e5", "#818cf8"),
            hover_color=("#c7d2fe", "#3730a3"),
            command=self._add_empty_group,
        )
        add_btn.pack(side="right")

        self.groups_container = ctk.CTkFrame(card, fg_color="transparent")
        self.groups_container.pack(fill="x", padx=8, pady=(0, 10))

    def _build_hall_settings_section(self, parent) -> None:
        """Section 3: Hall capacity and series columns (A, B, C)."""
        card = ctk.CTkFrame(parent, fg_color=("white", "#161d35"), corner_radius=10)
        card.pack(fill="x", padx=8, pady=5)

        ctk.CTkLabel(
            card, text="🏛️  Hall Settings",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 5))

        # Hall Capacity Entry
        cap_row = ctk.CTkFrame(card, fg_color="transparent")
        cap_row.pack(fill="x", padx=12, pady=(0, 2))
        ctk.CTkLabel(
            cap_row, text="CAPACITY PER YEAR PER HALL", font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60"), anchor="w",
        ).pack(side="left")
        self.capacity_entry = ctk.CTkEntry(cap_row, width=60, height=28, font=ctk.CTkFont(size=12))
        self.capacity_entry.pack(side="right")
        self.capacity_entry.insert(0, "12")

        ctk.CTkLabel(
            card, text="Default: 12 per year (36 total per hall)",
            font=ctk.CTkFont(size=9), text_color=("gray50", "gray60"), anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 8))

        # Dynamic Hall Series Columns (A, B, C)
        halls_grid = ctk.CTkFrame(card, fg_color="transparent")
        halls_grid.pack(fill="x", padx=8, pady=(0, 10))
        halls_grid.grid_columnconfigure((0, 1, 2), weight=1)

        self.hall_containers: Dict[str, ctk.CTkFrame] = {}
        for col_idx, prefix in enumerate(["A", "B", "C"]):
            col_frame = ctk.CTkFrame(halls_grid, fg_color=("gray95", "#111827"), corner_radius=6)
            col_frame.grid(row=0, column=col_idx, sticky="nsew", padx=3)

            col_header = ctk.CTkFrame(col_frame, fg_color="transparent")
            col_header.pack(fill="x", padx=4, pady=(4, 2))
            ctk.CTkLabel(
                col_header, text=f"Series {prefix}",
                font=ctk.CTkFont(size=10, weight="bold"),
            ).pack(side="left")

            ctk.CTkButton(
                col_header, text="+", width=20, height=20,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("#e0e7ff", "#2a2f55"),
                text_color=("#4f46e5", "#818cf8"),
                hover_color=("#c7d2fe", "#3730a3"),
                command=lambda p=prefix: self._add_hall(p),
            ).pack(side="right")

            items_frame = ctk.CTkFrame(col_frame, fg_color="transparent")
            items_frame.pack(fill="x", padx=4, pady=(0, 4))
            self.hall_containers[prefix] = items_frame

    def _build_action_buttons(self, parent) -> None:
        """Section 4: Primary actions (Generate & Clear)."""
        actions = ctk.CTkFrame(parent, fg_color="transparent")
        actions.pack(fill="x", padx=8, pady=(10, 8))

        ctk.CTkButton(
            actions,
            text="⚡  Generate Allotment",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color=("#4f46e5", "#4f46e5"),
            hover_color=("#4338ca", "#4338ca"),
            command=self._handle_generate,
        ).pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            actions,
            text="Clear Inputs",
            font=ctk.CTkFont(size=12),
            height=34,
            fg_color=("gray85", "#1e293b"),
            text_color=("gray30", "gray70"),
            hover_color=("gray75", "#334155"),
            command=self._handle_reset,
        ).pack(fill="x")

    # =========================================================================
    #  CONTENT AREA (TABS)
    # =========================================================================

    def _build_content_area(self) -> None:
        """Constructs the tabbed main view panel on the right."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(
            content,
            fg_color=("white", "#111827"),
            segmented_button_fg_color=("gray90", "#1e293b"),
            segmented_button_selected_color=("#4f46e5", "#4f46e5"),
            segmented_button_selected_hover_color=("#4338ca", "#4338ca"),
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        tab1 = self.tabview.add("Dashboard & Charts")
        self._build_dashboard_tab(tab1)

        tab2 = self.tabview.add("Master List")
        self.master_view = MasterListView(tab2)
        self.master_view.pack(fill="both", expand=True, padx=5, pady=5)

        tab3 = self.tabview.add("Instructions")
        self._build_instructions_tab(tab3)

    def _build_dashboard_tab(self, parent) -> None:
        """Builds overview statistics, hall selector, export dropdown, and seating visualizer."""
        # Top KPI Summary Cards
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.stat_labels: Dict[str, ctk.CTkLabel] = {}
        metrics = [
            ("Total Allocated", "total", "#4f46e5"),
            ("3rd Year", "y3", "#f59e0b"),
            ("2nd Year", "y2", "#10b981"),
            ("1st Year", "y1", "#3b82f6"),
            ("Halls Filled", "halls", "#6366f1"),
        ]
        for title, key, color in metrics:
            card = ctk.CTkFrame(stats_frame, fg_color=("gray97", "#161d35"), corner_radius=8)
            card.pack(side="left", expand=True, fill="x", padx=4)

            ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=0).pack(fill="x")
            ctk.CTkLabel(
                card, text=title, font=ctk.CTkFont(size=9),
                text_color=("gray50", "gray60"),
            ).pack(pady=(6, 0))

            val_label = ctk.CTkLabel(
                card, text="0", font=ctk.CTkFont(size=22, weight="bold"),
                text_color=("gray10", "gray90"),
            )
            val_label.pack(pady=(0, 8))
            self.stat_labels[key] = val_label

        # Controls row: Hall dropdown selector & Unified Export dropdown
        controls = ctk.CTkFrame(parent, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            controls, text="View Hall:", font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=(0, 5))

        self.hall_selector = ctk.CTkOptionMenu(
            controls,
            values=["No Allotment Generated"],
            width=200,
            height=32,
            command=self._on_hall_selected,
        )
        self.hall_selector.pack(side="left", padx=(0, 15))

        self.export_menu = ctk.CTkOptionMenu(
            controls,
            values=EXPORT_OPTIONS,
            width=220,
            height=32,
            fg_color=("#10b981", "#065f46"),
            button_color=("#059669", "#047857"),
            button_hover_color=("#047857", "#065f46"),
            command=self._handle_export_selected,
        )
        self.export_menu.pack(side="right")
        self.export_menu.set("📥  Export Options")

        # Interactive Classroom Seating Visualizer
        self.visualizer = HallVisualizer(parent, fg_color=("white", "#0f1525"), corner_radius=10)
        self.visualizer.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def _build_instructions_tab(self, parent) -> None:
        """Renders reference documentation on seating heuristics and export capabilities."""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        guide_sections = [
            ("1. Multi-Year Seating Allocation Heuristic",
             "Students are distributed such that each exam hall has a maximum capacity "
             "of 12 students per academic year (a total of 36 students per hall when full)."),

            ("2. Cheat Prevention Interleaved Seating",
             "Each classroom row consists of two separate desks (Left & Right) separated by an aisle:\n"
             "  • Left Desk (3 Seats): [1st Year | 2nd Year | 3rd Year]\n"
             "  • Right Desk (3 Seats): [1st Year | 2nd Year | 3rd Year]\n\n"
             "Students from the same academic year never sit on the same bench or adjacent to each other."),

            ("3. Flexible Register Number Formatting",
             "Two input modes are supported:\n"
             "  • Sequential Range: Starting roll number (e.g. 2226128001) + count.\n"
             "  • Raw Multi-Line List: Direct paste of register numbers, one per line."),

            ("4. Multi-Format Reporting & Export",
             "Generate ready-to-print documents in one click:\n"
             "  • Excel (.xlsx): Classroom visual layout or tabular master list.\n"
             "  • PDF (.pdf): Formatted, color-coded A4 landscape charts.\n"
             "  • CSV (.csv): Raw structured data for university ERP import."),
        ]

        for heading, body in guide_sections:
            ctk.CTkLabel(
                scroll, text=heading, font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#4f46e5", "#818cf8"), anchor="w",
            ).pack(fill="x", pady=(12, 4))

            ctk.CTkLabel(
                scroll, text=body, font=ctk.CTkFont(size=12),
                text_color=("gray30", "gray70"), anchor="w", justify="left", wraplength=700,
            ).pack(fill="x", pady=(0, 8))

    # =========================================================================
    #  STUDENT GROUP & HALL CARD MANAGEMENT
    # =========================================================================

    def _add_group_card(self, **kwargs) -> GroupCard:
        """Instantiates and registers an encapsulated student group card."""
        card = GroupCard(self.groups_container, on_delete=self._remove_group, **kwargs)
        card.pack(fill="x", padx=4, pady=4)
        self.group_cards.append(card)
        return card

    def _add_empty_group(self) -> None:
        """Adds a blank group configuration card."""
        self._add_group_card(department=DEGREES[0], year=3)
        show_toast(self, "New student group added.", "success")

    def _remove_group(self, card: GroupCard) -> None:
        """Removes and destroys a student group card."""
        if card in self.group_cards:
            self.group_cards.remove(card)
        card.destroy()
        show_toast(self, "Student group removed.", "success")

    def _collect_groups_data(self) -> List[Dict[str, Any]]:
        """Collects clean input dictionaries from each registered group card."""
        return [card.get_data() for card in self.group_cards]

    def _add_hall(self, prefix: str) -> None:
        """Appends a new numbered hall to series A, B, or C."""
        series = self.configured_halls[prefix]
        nums = [int(m.group()) for name in series if (m := re.search(r"\d+", name))]
        new_name = f"{prefix}{max(nums, default=0) + 1}"
        series.append(new_name)
        self._render_hall_badges()
        show_toast(self, f"Hall {new_name} added.", "success")

    def _remove_hall(self, prefix: str, name: str) -> None:
        """Removes a hall from the specified series."""
        if name in self.configured_halls[prefix]:
            self.configured_halls[prefix].remove(name)
            self._render_hall_badges()
            show_toast(self, f"Hall {name} removed.", "success")

    def _render_hall_badges(self) -> None:
        """Refreshes the dynamic hall pills in columns A, B, and C."""
        for prefix in ["A", "B", "C"]:
            container = self.hall_containers[prefix]
            for w in container.winfo_children():
                w.destroy()

            for name in self.configured_halls[prefix]:
                item = ctk.CTkFrame(container, fg_color=("gray90", "#1e293b"), corner_radius=4, height=24)
                item.pack(fill="x", pady=1)

                ctk.CTkLabel(
                    item, text=name, font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=("#4f46e5", "#818cf8"),
                ).pack(side="left", padx=6)

                ctk.CTkButton(
                    item, text="×", width=18, height=18, font=ctk.CTkFont(size=12),
                    fg_color="transparent", text_color=("gray50", "gray60"),
                    hover_color=("gray80", "#334155"),
                    command=lambda p=prefix, n=name: self._remove_hall(p, n),
                ).pack(side="right", padx=2)

    def _get_ordered_hall_names(self) -> List[str]:
        """Returns ordered list of hall names (e.g. A1, A2, B1, B2, C1)."""
        names = []
        for prefix in ["A", "B", "C"]:
            series = sorted(
                self.configured_halls[prefix],
                key=lambda n: int(m.group()) if (m := re.search(r"\d+", n)) else 0
            )
            names.extend(series)
        return names

    # =========================================================================
    #  CORE ALLOTMENT & EXPORT WORKFLOWS
    # =========================================================================

    def _handle_generate(self) -> None:
        """Executes student group parsing, seating allocation, and UI data binding."""
        groups_data = self._collect_groups_data()
        students = parse_student_groups(groups_data)
        total_students = len(students["y1"]) + len(students["y2"]) + len(students["y3"])

        if total_students == 0:
            show_toast(self, "Please enter roll numbers for at least one group.", "error")
            return

        try:
            capacity = int(self.capacity_entry.get().strip())
            if capacity <= 0:
                raise ValueError
        except ValueError:
            show_toast(self, "Please enter a valid capacity per year.", "error")
            return

        hall_names = self._get_ordered_hall_names()
        if not hall_names:
            show_toast(self, "Please configure at least one hall.", "error")
            return

        # Execute pure domain algorithm
        self.halls = allocate_seating(students, hall_names, capacity)

        # Persist updated state to JSON
        self.dm.save_halls(self.halls)
        self.dm.save_groups(groups_data)
        self.dm.save_settings({
            "college_name": self.college_name_entry.get(),
            "exam_title": self.exam_title_entry.get(),
            "capacity_per_year": capacity,
            "configured_halls": self.configured_halls,
        })

        # Update KPI cards
        self.stat_labels["total"].configure(text=str(total_students))
        self.stat_labels["y1"].configure(text=str(len(students["y1"])))
        self.stat_labels["y2"].configure(text=str(len(students["y2"])))
        self.stat_labels["y3"].configure(text=str(len(students["y3"])))
        self.stat_labels["halls"].configure(text=str(len(self.halls)))

        # Update hall selection dropdown
        hall_options = [f"{h['name']} ({h['stats']['total']} Students)" for h in self.halls]
        self.hall_selector.configure(values=hall_options)
        if hall_options:
            self.hall_selector.set(hall_options[0])

        # Render first hall and populate master notice table
        if self.halls:
            self.visualizer.render_hall(
                self.halls[0],
                self.college_name_entry.get(),
                self.exam_title_entry.get(),
            )

        master_records = build_master_list(self.halls)
        self.master_view.load_data(master_records)

        show_toast(self, "Seating allocation generated successfully!", "success")

    def _handle_reset(self) -> None:
        """Resets all settings, inputs, and UI widgets to clean default state."""
        for card in self.group_cards:
            card.destroy()
        self.group_cards.clear()

        self.configured_halls = {
            "A": list(DEFAULT_HALLS["A"]),
            "B": list(DEFAULT_HALLS["B"]),
            "C": list(DEFAULT_HALLS["C"]),
        }
        self._render_hall_badges()

        for g in DEFAULT_GROUPS:
            self._add_group_card(**g)

        self.college_name_entry.delete(0, "end")
        self.college_name_entry.insert(0, "ANANDA COLLEGE OF ARTS & SCIENCE")
        self.exam_title_entry.delete(0, "end")
        self.exam_title_entry.insert(0, "Semester End Examinations - April 2026")
        self.capacity_entry.delete(0, "end")
        self.capacity_entry.insert(0, "12")

        self.halls = []
        for key in self.stat_labels:
            self.stat_labels[key].configure(text="0")

        self.hall_selector.configure(values=["No Allotment Generated"])
        self.hall_selector.set("No Allotment Generated")
        self.visualizer.clear()
        self.master_view.clear()

        self.dm.clear_all()
        show_toast(self, "All inputs cleared.", "success")

    def _on_hall_selected(self, option_text: str) -> None:
        """Renders the selected hall layout when the user toggles the dropdown."""
        hall_name = option_text.split(" (")[0].strip()
        hall = next((h for h in self.halls if h["name"] == hall_name), None)
        if hall:
            self.visualizer.render_hall(
                hall,
                self.college_name_entry.get(),
                self.exam_title_entry.get(),
            )

    def _get_current_hall(self) -> Optional[Dict[str, Any]]:
        """Retrieves the dictionary of the currently viewed hall."""
        selected = self.hall_selector.get()
        hall_name = selected.split(" (")[0].strip()
        return next((h for h in self.halls if h["name"] == hall_name), None)

    def _handle_export_selected(self, choice: str) -> None:
        """Routes the chosen export format to the ExportService."""
        current_hall = self._get_current_hall()
        college = self.college_name_entry.get()
        exam = self.exam_title_entry.get()

        success, message = ExportService.handle_export(
            choice=choice,
            halls=self.halls,
            current_hall=current_hall,
            college_name=college,
            exam_title=exam,
        )

        if message:
            show_toast(self, message, "success" if success else "error")

        # Reset dropdown label
        self.export_menu.set("📥  Export Options")

    # =========================================================================
    #  DATA PERSISTENCE / STARTUP
    # =========================================================================

    def _load_saved_data(self) -> None:
        """Restores previously saved state from disk upon application launch."""
        settings = self.dm.load_settings()
        if settings:
            if "college_name" in settings:
                self.college_name_entry.delete(0, "end")
                self.college_name_entry.insert(0, settings["college_name"])
            if "exam_title" in settings:
                self.exam_title_entry.delete(0, "end")
                self.exam_title_entry.insert(0, settings["exam_title"])
            if "capacity_per_year" in settings:
                self.capacity_entry.delete(0, "end")
                self.capacity_entry.insert(0, str(settings["capacity_per_year"]))
            self.configured_halls = settings.get("configured_halls", {
                "A": list(DEFAULT_HALLS["A"]),
                "B": list(DEFAULT_HALLS["B"]),
                "C": list(DEFAULT_HALLS["C"]),
            })
        else:
            self.configured_halls = {
                "A": list(DEFAULT_HALLS["A"]),
                "B": list(DEFAULT_HALLS["B"]),
                "C": list(DEFAULT_HALLS["C"]),
            }

        self._render_hall_badges()

        # Restore group cards
        saved_groups = self.dm.load_groups()
        groups_to_load = saved_groups if saved_groups else DEFAULT_GROUPS
        for group in groups_to_load:
            self._add_group_card(**group)
        # Leave seating visualizer and master list empty until user clicks 'Generate Allotment'
        self.halls = []
