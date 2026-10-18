"""
group_card.py — Self-contained UI card for student group configuration.

Encapsulates:
  - Department and Year selection dropdowns
  - Start roll and total count entry fields
  - Expandable multi-line raw roll number input
  - Year-specific border accent colors
  - Direct data serialization via `get_data()`
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any, List
from app.constants import DEGREES


# Color mappings for the card border based on academic year
YEAR_BORDER_COLORS: Dict[int, str] = {
    1: "#3b82f6",  # Blue (UG 1)
    2: "#10b981",  # Emerald (UG 2)
    3: "#f59e0b",  # Amber (UG 3)
    4: "#3b82f6",  # Blue (PG 1)
    5: "#10b981",  # Emerald (PG 2)
}

YEAR_LABEL_TO_INT: Dict[str, int] = {
    "1st Year (UG)": 1,
    "2nd Year (UG)": 2,
    "3rd Year (UG)": 3,
    "1st Year (PG)": 4,
    "2nd Year (PG)": 5,
}

YEAR_INT_TO_LABEL: Dict[int, str] = {v: k for k, v in YEAR_LABEL_TO_INT.items()}


class GroupCard(ctk.CTkFrame):
    """
    A modular UI card allowing configuration of a single student group.
    """

    def __init__(
        self,
        parent,
        department: str = DEGREES[0],
        year: int = 3,
        start_roll: str = "",
        count: str = "",
        raw_list: str = "",
        exempt_checked: bool = False,
        excluded_rolls: Optional[List[str]] = None,
        on_delete: Optional[Callable[["GroupCard"], None]] = None,
        **kwargs,
    ):
        border_color = YEAR_BORDER_COLORS.get(year, "#6366f1")
        super().__init__(
            parent,
            fg_color=("white", "#12182d"),
            corner_radius=8,
            border_width=2,
            border_color=border_color,
            **kwargs,
        )

        self.on_delete = on_delete
        self.excluded_rolls: List[str] = excluded_rolls or []
        self._raw_visible = bool(raw_list.strip())

        self._build_header(department, year)
        self._build_body(start_roll, count)
        self._build_raw_input(raw_list)
        self._build_footer(exempt_checked)

    def _build_header(self, department: str, year: int) -> None:
        """Top row: Department dropdown, Academic Year dropdown, Delete button."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 4))

        # Department selector
        self.dept_menu = ctk.CTkOptionMenu(
            header,
            values=DEGREES,
            width=150,
            height=26,
            font=ctk.CTkFont(size=11),
        )
        self.dept_menu.pack(side="left", padx=(0, 4))
        self.dept_menu.set(department if department in DEGREES else DEGREES[0])

        # Academic Year selector
        year_options = list(YEAR_LABEL_TO_INT.keys())
        self.year_menu = ctk.CTkOptionMenu(
            header,
            values=year_options,
            width=120,
            height=26,
            font=ctk.CTkFont(size=11),
            command=self._on_year_changed,
        )
        self.year_menu.pack(side="left", padx=(0, 4))
        self.year_menu.set(YEAR_INT_TO_LABEL.get(year, "3rd Year (UG)"))

        # Delete button
        del_btn = ctk.CTkButton(
            header,
            text="🗑",
            width=26,
            height=26,
            fg_color=("gray90", "#1e293b"),
            text_color=("#ef4444", "#ef4444"),
            hover_color=("#fecaca", "#450a0a"),
            font=ctk.CTkFont(size=13),
            command=self._handle_delete,
        )
        del_btn.pack(side="right")

    def _build_body(self, start_roll: str, count: str) -> None:
        """Middle row: Starting Roll Number and Total Count entries."""
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=8, pady=(0, 4))

        # Start roll input column
        left_col = ctk.CTkFrame(body, fg_color="transparent")
        left_col.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkLabel(
            left_col, text="START ROLL", font=ctk.CTkFont(size=9),
            text_color=("gray50", "gray60"), anchor="w",
        ).pack(fill="x")
        self.start_entry = ctk.CTkEntry(left_col, height=26, font=ctk.CTkFont(size=11))
        self.start_entry.pack(fill="x")
        self.start_entry.insert(0, start_roll)

        # Count input column
        right_col = ctk.CTkFrame(body, fg_color="transparent")
        right_col.pack(side="left", fill="x", expand=True, padx=(4, 0))
        ctk.CTkLabel(
            right_col, text="TOTAL COUNT", font=ctk.CTkFont(size=9),
            text_color=("gray50", "gray60"), anchor="w",
        ).pack(fill="x")
        self.count_entry = ctk.CTkEntry(right_col, height=26, font=ctk.CTkFont(size=11))
        self.count_entry.pack(fill="x")
        self.count_entry.insert(0, count)

    def _build_raw_input(self, initial_text: str) -> None:
        """Optional raw roll number textarea (useful when rolls are non-consecutive)."""
        self.raw_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.raw_frame.pack(fill="x", padx=8, pady=(2, 4))

        self.raw_textbox = ctk.CTkTextbox(
            self.raw_frame,
            height=60,
            font=ctk.CTkFont(size=10),
            fg_color=("gray95", "#0f1525"),
        )
        if initial_text.strip():
            self.raw_textbox.insert("1.0", initial_text)
            self.raw_textbox.pack(fill="x", pady=(4, 0))

        toggle_btn = ctk.CTkButton(
            self.raw_frame,
            text="Toggle Raw List Input",
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            text_color=("#4f46e5", "#818cf8"),
            hover_color=("gray90", "#1e293b"),
            height=22,
            width=140,
            anchor="w",
            command=self._toggle_raw_list,
        )
        toggle_btn.pack(anchor="w")

    def _build_footer(self, exempt_checked: bool) -> None:
        """Footer: Exemption toggle checkbox."""
        self.exempt_var = ctk.BooleanVar(value=exempt_checked)
        self.exempt_cb = ctk.CTkCheckBox(
            self,
            text="Exempt individual students",
            variable=self.exempt_var,
            font=ctk.CTkFont(size=10),
            height=20,
        )
        self.exempt_cb.pack(anchor="w", padx=8, pady=(0, 8))

    def _on_year_changed(self, selected_label: str) -> None:
        """Dynamically update border color based on the selected academic year."""
        year = YEAR_LABEL_TO_INT.get(selected_label, 3)
        self.configure(border_color=YEAR_BORDER_COLORS.get(year, "#6366f1"))

    def _toggle_raw_list(self) -> None:
        """Show or hide the raw roll list text box."""
        if self.raw_textbox.winfo_manager():
            self.raw_textbox.pack_forget()
            self._raw_visible = False
        else:
            self.raw_textbox.pack(fill="x", pady=(4, 0))
            self._raw_visible = True

    def _handle_delete(self) -> None:
        """Notify parent container to destroy this card."""
        if self.on_delete:
            self.on_delete(self)
        else:
            self.destroy()

    def get_data(self) -> Dict[str, Any]:
        """
        Extract clean, validated data from UI inputs into a plain dictionary.
        This completely eliminates ad-hoc widget scraping from parent containers.
        """
        year = YEAR_LABEL_TO_INT.get(self.year_menu.get(), 3)
        raw_text = self.raw_textbox.get("1.0", "end").strip() if self._raw_visible else ""

        return {
            "department": self.dept_menu.get(),
            "year": year,
            "start_roll": self.start_entry.get().strip(),
            "count": self.count_entry.get().strip(),
            "raw_list": raw_text,
            "exempt_checked": self.exempt_var.get(),
            "excluded_rolls": self.excluded_rolls,
        }
