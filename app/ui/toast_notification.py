"""
toast_notification.py — A small pop-up message that appears briefly.

In the original web app, toasts slid in from the bottom-right corner.
This module recreates that behavior using a CTkFrame that appears
inside the main window, then fades away after a few seconds.

Usage:
    show_toast(parent_widget, "Allotment generated!", "success")
    show_toast(parent_widget, "Invalid input!", "error")
"""

import customtkinter as ctk


class ToastNotification(ctk.CTkFrame):
    """
    A temporary notification bar that shows a message and auto-disappears.

    Parameters
    ----------
    parent   : the parent widget (usually the main window)
    message  : text to display
    toast_type : "success" (green accent) or "error" (red accent)
    duration : milliseconds before the toast disappears (default 3500)
    """

    def __init__(
        self,
        parent,
        message: str,
        toast_type: str = "success",
        duration: int = 3500,
    ):
        super().__init__(parent)

        # Pick the accent color based on type.
        if toast_type == "error":
            accent_color = "#ef4444"
        else:
            accent_color = "#10b981"

        # Configure the toast frame appearance.
        self.configure(
            corner_radius=8,
            fg_color=("white", "#1e293b"),
            border_width=1,
            border_color=("gray80", "gray30"),
        )

        # A thin colored stripe on the left side (simulated with a small frame).
        stripe = ctk.CTkFrame(
            self,
            width=4,
            height=40,
            corner_radius=2,
            fg_color=accent_color,
        )
        stripe.pack(side="left", padx=(8, 0), pady=8)

        # The message text.
        label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray20", "gray90"),
            anchor="w",
        )
        label.pack(side="left", padx=(10, 16), pady=10)

        # Place the toast at the bottom-right of the parent window.
        self.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

        # Bring it to the front so it's visible over other widgets.
        self.lift()

        # Schedule auto-dismiss.
        self.after(duration, self._dismiss)

    def _dismiss(self):
        """Remove the toast from the screen."""
        try:
            self.destroy()
        except Exception:
            pass  # Widget might already be destroyed if window closed.


# ---------------------------------------------------------------------------
# Convenience function (the one you'll actually call most of the time)
# ---------------------------------------------------------------------------

def show_toast(parent, message: str, toast_type: str = "success", duration: int = 3500):
    """
    Show a brief notification message on the screen.

    Parameters
    ----------
    parent     : any widget — the toast will be placed in its top-level window
    message    : the text to show
    toast_type : "success" or "error"
    duration   : auto-dismiss time in milliseconds
    """
    # Find the top-level window so the toast always appears there.
    top = parent.winfo_toplevel()
    ToastNotification(top, message, toast_type, duration)
