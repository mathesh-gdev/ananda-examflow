"""
csv_exporter.py — Export seating data to CSV files.

CSV is a simple text format that can be opened in Excel, Google Sheets,
or any text editor.  This module uses Python's built-in `csv` library
(no extra installs needed).

Two export modes:
  1. Single hall layout (flat table)
  2. Master list (sorted table of all students)
"""

import csv

from app.constants import YEARS
from app.allotment_engine import build_master_list


def export_hall_csv(hall: dict, filepath: str) -> None:
    """
    Export one hall's seating data as a CSV file.

    Columns: Row, Desk, Seat Position, Roll Number, Year, Seat Number
    """
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header row
        writer.writerow([
            "Row", "Desk", "Seat Position", "Roll Number", "Year", "Seat Number"
        ])

        for row in hall["rows"]:
            # Left desk seats
            for idx, seat in enumerate(row["left_desk"]):
                if seat:
                    year_label = YEARS.get(seat["year"], {}).get("label", "")
                    writer.writerow([
                        row["row_num"],
                        "Left",
                        idx + 1,
                        seat["roll"],
                        year_label,
                        seat["seat_no"],
                    ])

            # Right desk seats
            for idx, seat in enumerate(row["right_desk"]):
                if seat:
                    year_label = YEARS.get(seat["year"], {}).get("label", "")
                    writer.writerow([
                        row["row_num"],
                        "Right",
                        idx + 1,
                        seat["roll"],
                        year_label,
                        seat["seat_no"],
                    ])


def export_master_csv(halls: list[dict], filepath: str) -> None:
    """
    Export the full master list of all student allocations as CSV.

    Columns: S.No, Register Number, Academic Year, Allocated Hall, Seat Location
    """
    records = build_master_list(halls)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header row
        writer.writerow([
            "S.No", "Register Number", "Academic Year",
            "Allocated Hall", "Seat Location",
        ])

        for i, record in enumerate(records, start=1):
            year_label = YEARS.get(record["year"], {}).get("label", "")
            writer.writerow([
                i,
                record["roll"],
                year_label,
                record["hall"],
                record["location"],
            ])
