"""
app_window.py — The main application window.

This is the top-level window that holds:
  - A header bar with the app logo, title, and theme toggle button
  - The AdminDashboard as the main content area

It's the first thing that appears when you launch the app.
"""

import customtkinter as ctk

from app.data_manager import DataManager
from app.ui.admin_dashboard import AdminDashboard


class AppWindow(ctk.CTk):
    """
    The main application window for Ananda Exam Cell.

    Responsibilities:
      - Set up the window title, size, and appearance
      - Create the header bar with logo and theme toggle
      - Host the AdminDashboard as the primary content
    """

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Ananda ExamFlow — Automated Seating Allotment Engine")
        self.geometry("1320x800")
        self.minsize(1000, 600)

        # Set the default appearance (dark mode, like the web app)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Data manager instance (shared across all UI components)
        self.data_manager = DataManager()

        # Build UI
        self._build_header()
        self._build_content()

    def _build_header(self):
        """Create the top header bar with logo, title, and theme toggle."""
        header = ctk.CTkFrame(
            self,
            height=55,
            fg_color=("white", "#0f1525"),
            corner_radius=0,
            border_width=1,
            border_color=("gray85", "#1e293b"),
        )
        header.pack(fill="x")
        header.pack_propagate(False)  # keep fixed height

        # Logo badge ("AE")
        logo = ctk.CTkLabel(
            header,
            text="AE",
            width=36,
            height=36,
            corner_radius=8,
            fg_color=("#4f46e5", "#4f46e5"),
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        logo.pack(side="left", padx=(16, 8), pady=10)

        # App title + subtitle
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(
            title_frame,
            text="Ananda ExamFlow",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Automated Seating Allotment Engine",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60"),
        ).pack(anchor="w")

        # Theme toggle button (right side)
        self._theme_btn = ctk.CTkButton(
            header,
            text="🌙  Dark",
            width=90,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=("gray90", "#1e293b"),
            text_color=("gray30", "gray70"),
            hover_color=("gray80", "#334155"),
            command=self._toggle_theme,
        )
        self._theme_btn.pack(side="right", padx=16, pady=10)

    def _build_content(self):
        """Create the admin dashboard as the main content."""
        self.dashboard = AdminDashboard(
            self,
            data_manager=self.data_manager,
        )
        self.dashboard.pack(fill="both", expand=True)

    def _toggle_theme(self):
        """Switch between dark and light themes."""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self._theme_btn.configure(text="☀️  Light")
        else:
            ctk.set_appearance_mode("dark")
            self._theme_btn.configure(text="🌙  Dark")
