"""
main.py — Entry point for the Ananda ExamFlow Desktop Application.

Run this file to start the application:
    python main.py

That's it! The app will open a window with the full admin dashboard
where you can configure students, halls, generate seating plans,
and export to Excel, PDF, or CSV.
"""

from app.ui.app_window import AppWindow


def main():
    """Create and start the application."""
    app = AppWindow()
    app.mainloop()


# This block runs when you execute the file directly: python main.py
if __name__ == "__main__":
    main()
