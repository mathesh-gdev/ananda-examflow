"""
hall_visualizer.py — The classroom seating grid widget.

Draws a visual representation of an exam hall:
  - "FRONT / BOARD" banner at the top
  - Rows of seats, each row split into Left Desk | Row# | Right Desk
  - Each seat is color-coded by academic year
  - Hover tooltips show full seat details

This is the most visually complex widget in the application.
It recreates the HTML seating grid from admin.html.
"""

import customtkinter as ctk


# Year → color mappings (used for seat backgrounds)
YEAR_COLORS = {
    1: {"bg": ("#dbeafe", "#1e3a5f"), "fg": ("#1d4ed8", "#93c5fd"), "label": "Y1"},
    2: {"bg": ("#d1fae5", "#0f3d2e"), "fg": ("#047857", "#6ee7b7"), "label": "Y2"},
    3: {"bg": ("#fef3c7", "#3d2e0a"), "fg": ("#b45309", "#fcd34d"), "label": "Y3"},
    4: {"bg": ("#dbeafe", "#1e3a5f"), "fg": ("#1d4ed8", "#93c5fd"), "label": "PG1"},
    5: {"bg": ("#d1fae5", "#0f3d2e"), "fg": ("#047857", "#6ee7b7"), "label": "PG2"},
}

EMPTY_COLORS = {
    "bg": ("#f1f5f9", "#1a1f30"),
    "fg": ("#94a3b8", "#4b5563"),
}


class HallVisualizer(ctk.CTkScrollableFrame):
    """
    A scrollable frame that displays the classroom seating grid for one hall.

    Usage:
        viz = HallVisualizer(parent)
        viz.render_hall(hall_dict)   # draw the seats
        viz.clear()                  # reset to empty state
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._tooltip_window = None  # Track active tooltip

        # Start with the empty state message.
        self._show_empty_state()

    def _show_empty_state(self):
        """Show a placeholder message when no hall is loaded."""
        self._clear_children()
        msg = ctk.CTkLabel(
            self,
            text="📋  Configure students and halls on the left,\nthen click 'Generate Allotment' to see the seating grid.",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60"),
            justify="center",
        )
        msg.pack(pady=60, padx=20)

    def _clear_children(self):
        """Remove all child widgets."""
        for widget in self.winfo_children():
            widget.destroy()

    def clear(self):
        """Public method to reset to empty state."""
        self._show_empty_state()

    def render_hall(self, hall: dict, college_name: str = "", exam_title: str = ""):
        """
        Draw the full classroom layout for the given hall.

        Parameters
        ----------
        hall : dict with "name", "rows", "stats" from the allotment engine
        college_name : displayed above the grid
        exam_title : displayed below college name
        """
        self._clear_children()

        # College / Exam banner (matches college-preview-banner from admin.html)
        if college_name:
            ctk.CTkLabel(
                self,
                text=college_name.upper(),
                font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                text_color=("gray10", "gray90"),
            ).pack(pady=(10, 2))

        if exam_title:
            ctk.CTkLabel(
                self,
                text=exam_title,
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray60"),
            ).pack(pady=(0, 2))

        # Hall name
        ctk.CTkLabel(
            self,
            text=f"Seating Plan: Hall {hall['name']}",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray50"),
        ).pack(pady=(0, 10))

        # "FRONT / BOARD" banner
        board_frame = ctk.CTkFrame(
            self,
            fg_color=("gray90", "#1a1f30"),
            corner_radius=6,
            border_width=1,
            border_color=("gray80", "gray30"),
            height=30,
        )
        board_frame.pack(fill="x", padx=40, pady=(5, 15))
        ctk.CTkLabel(
            board_frame,
            text="FRONT / BOARD / INSTRUCTOR DESK",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray50", "gray60"),
        ).pack(pady=6)

        # Seat rows
        for row in hall["rows"]:
            self._draw_row(row)

        # Legend bar at the bottom
        self._draw_legend()

    def _draw_row(self, row: dict):
        """Draw a single row: [Left Desk] [Row#] [Right Desk]."""
        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(fill="x", padx=20, pady=3)

        # Use grid for left-center-right alignment.
        row_frame.grid_columnconfigure(0, weight=1)  # left desk
        row_frame.grid_columnconfigure(1, weight=0)  # row label
        row_frame.grid_columnconfigure(2, weight=1)  # right desk

        # Left desk (3 seats in a horizontal group)
        left_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="e", padx=(0, 10))
        for idx, seat in enumerate(row["left_desk"]):
            desk_label = f"Row {row['row_num']} - Left Desk - Seat {idx + 1}"
            self._draw_seat(left_frame, seat, desk_label, idx)

        # Row number circle in the center
        row_label = ctk.CTkLabel(
            row_frame,
            text=str(row["row_num"]),
            width=28,
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("gray90", "#1e293b"),
            text_color=("gray50", "gray60"),
        )
        row_label.grid(row=0, column=1, padx=5)

        # Right desk (3 seats)
        right_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="w", padx=(10, 0))
        for idx, seat in enumerate(row["right_desk"]):
            desk_label = f"Row {row['row_num']} - Right Desk - Seat {idx + 1}"
            self._draw_seat(right_frame, seat, desk_label, idx)

    def _draw_seat(self, parent, seat, location_text: str, column: int):
        """
        Draw a single seat cell.

        Each seat is a small square label with:
          - Background color based on the student's year
          - The roll number (truncated to last 4 digits for space)
          - A tooltip on hover showing the full details
        """
        if seat is None:
            # Empty seat — dashed-look, muted colors
            seat_frame = ctk.CTkLabel(
                parent,
                text="—",
                width=70,
                height=50,
                corner_radius=6,
                fg_color=EMPTY_COLORS["bg"],
                text_color=EMPTY_COLORS["fg"],
                font=ctk.CTkFont(size=10),
            )
        else:
            year = seat["year"]
            colors = YEAR_COLORS.get(year, YEAR_COLORS[3])

            # Show the last few characters of the roll number to fit.
            roll_display = seat["roll"]
            if len(roll_display) > 8:
                roll_display = "..." + roll_display[-6:]

            year_label = colors["label"]
            seat_text = f"{roll_display}\n{year_label} S:{seat['seat_no']}"

            seat_frame = ctk.CTkLabel(
                parent,
                text=seat_text,
                width=70,
                height=50,
                corner_radius=6,
                fg_color=colors["bg"],
                text_color=colors["fg"],
                font=ctk.CTkFont(size=9, weight="bold"),
                anchor="center",
                justify="center",
            )

            # Tooltip data stored for hover event.
            full_tooltip = (
                f"{location_text}\n"
                f"Roll: {seat['roll']}\n"
                f"Year: {year_label}\n"
                f"Seat No: {seat['seat_no']}"
            )
            seat_frame.bind("<Enter>", lambda e, t=full_tooltip: self._show_tooltip(e, t))
            seat_frame.bind("<Leave>", lambda e: self._hide_tooltip())

        seat_frame.grid(row=0, column=column, padx=2, pady=2)

    def _show_tooltip(self, event, text: str):
        """Display a floating tooltip near the mouse cursor."""
        self._hide_tooltip()  # clear any existing one

        x = event.widget.winfo_rootx() + 30
        y = event.widget.winfo_rooty() - 10

        self._tooltip_window = tw = ctk.CTkToplevel()
        tw.wm_overrideredirect(True)  # No title bar
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        label = ctk.CTkLabel(
            tw,
            text=text,
            font=ctk.CTkFont(size=11),
            fg_color=("gray95", "#0f172a"),
            text_color=("gray10", "gray90"),
            corner_radius=6,
            padx=10,
            pady=6,
            justify="left",
            anchor="w",
        )
        label.pack()

    def _hide_tooltip(self):
        """Remove the floating tooltip."""
        if self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None

    def _draw_legend(self):
        """Draw the color legend bar at the bottom of the grid."""
        legend_frame = ctk.CTkFrame(
            self,
            fg_color=("gray95", "#111827"),
            corner_radius=6,
            border_width=1,
            border_color=("gray85", "gray30"),
        )
        legend_frame.pack(fill="x", padx=40, pady=(15, 10))

        items = [
            ("■  1st Year (Y1)", "#3b82f6"),
            ("■  2nd Year (Y2)", "#10b981"),
            ("■  3rd Year (Y3)", "#f59e0b"),
            ("—  Empty Seat",    "gray50"),
        ]
        inner = ctk.CTkFrame(legend_frame, fg_color="transparent")
        inner.pack(pady=8)
        for text, color in items:
            ctk.CTkLabel(
                inner,
                text=text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color,
            ).pack(side="left", padx=12)
