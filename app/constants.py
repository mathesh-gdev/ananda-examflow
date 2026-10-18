"""
constants.py — All fixed values used across the application.

This file holds color definitions, year configurations, degree lists,
and default hall setups. Think of it as a central "settings dictionary"
that every other module imports from.
"""

# ---------------------------------------------------------------------------
# YEAR CONFIGURATIONS
# Maps year number → human label + short label + color key
# Year 1-3 are UG (Undergraduate), 4-5 are PG (Postgraduate).
# In the seating algorithm, years 1 & 4 share slot "y1",
# years 2 & 5 share slot "y2", and year 3 uses slot "y3".
# ---------------------------------------------------------------------------
YEARS = {
    1: {"label": "1st Year (UG)", "short": "Yr 1",     "slot": "y1"},
    2: {"label": "2nd Year (UG)", "short": "Yr 2",     "slot": "y2"},
    3: {"label": "3rd Year (UG)", "short": "Yr 3",     "slot": "y3"},
    4: {"label": "1st Year (PG)", "short": "Yr 1 (PG)", "slot": "y1"},
    5: {"label": "2nd Year (PG)", "short": "Yr 2 (PG)", "slot": "y2"},
}

# ---------------------------------------------------------------------------
# DEPARTMENT / DEGREE OPTIONS
# These appear in the dropdown when the user adds a student group.
# ---------------------------------------------------------------------------
DEGREES = [
    "BA Tamil",
    "BA English",
    "BA Maths",
    "BCom",
    "BCom CA",
    "B.Com Accounts and Finance",
    "BBA",
    "BCA",
    "BSC Computer Science",
    "BSC Physics",
    "BSC Chemistry",
    "BSC Data Science",
    "Msc - IT",
    "M.Com",
    "M.com CA",
    "MSW",
]

# ---------------------------------------------------------------------------
# COLOR PALETTE
# Two themes: "dark" and "light".  Each theme defines background, text,
# accent colors, and per-year seat colors (matching the original web CSS).
# ---------------------------------------------------------------------------
COLORS = {
    "dark": {
        # Backgrounds
        "bg_primary":      "#0a0f1d",
        "bg_secondary":    "#12182d",
        "bg_card":         "#161d35",
        "border":          "#2a2f45",

        # Text
        "text_primary":    "#f3f4f6",
        "text_secondary":  "#9ca3af",
        "text_muted":      "#6b7280",

        # Accent colours
        "primary":         "#6366f1",   # Indigo
        "primary_hover":   "#4f46e5",
        "accent":          "#10b981",   # Emerald

        # Year seat colours
        "year_1":          "#3b82f6",   # Blue
        "year_1_bg":       "#1e3a5f",
        "year_2":          "#10b981",   # Emerald
        "year_2_bg":       "#0f3d2e",
        "year_3":          "#f59e0b",   # Amber
        "year_3_bg":       "#3d2e0a",

        # Empty seat
        "empty_bg":        "#1a1f30",
        "empty_border":    "#2a2f45",
        "empty_text":      "#4b5563",

        # Status
        "success":         "#10b981",
        "error":           "#ef4444",
    },
    "light": {
        "bg_primary":      "#f8fafc",
        "bg_secondary":    "#ffffff",
        "bg_card":         "#ffffff",
        "border":          "#e2e8f0",

        "text_primary":    "#0f172a",
        "text_secondary":  "#475569",
        "text_muted":      "#94a3b8",

        "primary":         "#4f46e5",
        "primary_hover":   "#4338ca",
        "accent":          "#059669",

        "year_1":          "#2563eb",
        "year_1_bg":       "#dbeafe",
        "year_2":          "#059669",
        "year_2_bg":       "#d1fae5",
        "year_3":          "#d97706",
        "year_3_bg":       "#fef3c7",

        "empty_bg":        "#f1f5f9",
        "empty_border":    "#e2e8f0",
        "empty_text":      "#cbd5e1",

        "success":         "#059669",
        "error":           "#dc2626",
    },
}

# ---------------------------------------------------------------------------
# DEFAULT HALL CONFIGURATION
# When the app starts fresh (no saved data), these halls are pre-populated.
# Each hall belongs to a "series" (A, B, or C).
# ---------------------------------------------------------------------------
DEFAULT_HALLS = {
    "A": ["A1", "A2"],
    "B": ["B1", "B2"],
    "C": ["C1", "C2"],
}

# ---------------------------------------------------------------------------
# DEFAULT STUDENT GROUPS
# Pre-filled sample data so the user can see the tool in action immediately.
# ---------------------------------------------------------------------------
DEFAULT_GROUPS = [
    {
        "department": "BSC Computer Science",
        "year": 3,
        "start_roll": "2224128001",
        "count": "29",
        "raw_list": "",
        "exempt_checked": False,
        "excluded_rolls": [],
    },
    {
        "department": "BSC Physics",
        "year": 2,
        "start_roll": "2225128001",
        "count": "25",
        "raw_list": "",
        "exempt_checked": False,
        "excluded_rolls": [],
    },
    {
        "department": "BSC Chemistry",
        "year": 1,
        "start_roll": "2226128001",
        "count": "27",
        "raw_list": "",
        "exempt_checked": False,
        "excluded_rolls": [],
    },
]
