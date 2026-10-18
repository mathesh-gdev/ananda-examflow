"""
data_manager.py — Handles saving and loading application data to JSON files.

In the original web app, all data was stored in the browser's localStorage.
This module replaces that with simple JSON files inside a `data/` folder
next to the application.

Files managed:
  data/halls.json     — The generated seating allotment (list of hall objects)
  data/groups.json    — Student group configurations entered by the user
  data/settings.json  — College name, exam title, configured hall names
"""

import json
import os


class DataManager:
    """
    Reads and writes application data to JSON files.

    Usage:
        dm = DataManager()          # auto-creates data/ folder
        dm.save_halls(halls_list)   # write halls to disk
        halls = dm.load_halls()     # read halls back
    """

    def __init__(self, data_dir: str = None):
        """
        Parameters
        ----------
        data_dir : str, optional
            Path to the data directory.  Defaults to a `data/` folder
            located next to the main application file.
        """
        if data_dir is None:
            # Figure out where the app lives and put data/ beside it.
            app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(app_root, "data")

        self.data_dir = data_dir
        # Create the folder if it doesn't exist yet.
        os.makedirs(self.data_dir, exist_ok=True)

    # -- Internal helpers ---------------------------------------------------

    def _filepath(self, filename: str) -> str:
        """Build the full path for a data file."""
        return os.path.join(self.data_dir, filename)

    def _save(self, filename: str, data) -> None:
        """Write any JSON-serializable object to a file."""
        path = self._filepath(filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load(self, filename: str, default=None):
        """Read a JSON file.  Returns `default` if the file doesn't exist."""
        path = self._filepath(filename)
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -- Hall Allotment Data -----------------------------------------------

    def save_halls(self, halls: list[dict]) -> None:
        """Save the generated seating allotment (list of hall objects)."""
        self._save("halls.json", halls)

    def load_halls(self) -> list[dict]:
        """Load the seating allotment.  Returns [] if no data saved."""
        return self._load("halls.json", default=[])

    # -- Student Group Configurations --------------------------------------

    def save_groups(self, groups: list[dict]) -> None:
        """Save the student group input configurations."""
        self._save("groups.json", groups)

    def load_groups(self) -> list[dict]:
        """Load saved student groups.  Returns [] if none saved."""
        return self._load("groups.json", default=[])

    # -- Settings (college name, exam title, hall config) -------------------

    def save_settings(self, settings: dict) -> None:
        """
        Save general settings.  Expected keys:
          - college_name (str)
          - exam_title (str)
          - capacity_per_year (int)
          - configured_halls (dict)  e.g. {"A": ["A1","A2"], "B": [...]}
        """
        self._save("settings.json", settings)

    def load_settings(self) -> dict:
        """Load settings.  Returns empty dict if none saved."""
        return self._load("settings.json", default={})

    # -- Utility -----------------------------------------------------------

    def clear_all(self) -> None:
        """Delete all saved data files (used by the 'Clear Inputs' button)."""
        for filename in ["halls.json", "groups.json", "settings.json"]:
            path = self._filepath(filename)
            if os.path.exists(path):
                os.remove(path)
