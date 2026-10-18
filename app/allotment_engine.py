"""
allotment_engine.py — Core seating allocation algorithm and student group parsing.

This module contains pure, deterministic domain logic with zero GUI dependencies.
It is 100% testable through standard unit tests.

Algorithm Overview (Cheat-Prevention Seating Design):
  1. Student Slotting: Students are grouped into 3 slots by academic year (y1, y2, y3).
  2. Sorting: Each slot is sorted alphabetically/numerically by register number.
  3. Hall Slicing: Each exam hall receives up to `capacity_per_year` students from EACH
     of the 3 slots (e.g., 12 from y1, 12 from y2, 12 from y3 = 36 per hall).
  4. Interleaved Desk Placement:
     - Each classroom row has two desks: Left Desk and Right Desk.
     - Each desk contains 3 seats: [Year 1, Year 2, Year 3].
     - Students from the same academic year are NEVER seated adjacent to one another.
  5. Vertical Seat Numbering:
     - Year 1 seats: 1–12 (Left desk rows 1–6, then Right desk rows 1–6)
     - Year 2 seats: 13–24 (Left desk rows 1–6, then Right desk rows 1–6)
     - Year 3 seats: 25–36 (Left desk rows 1–6, then Right desk rows 1–6)
"""

import math
import re
from typing import List, Dict, Any, Optional
from app.constants import YEARS


def generate_sequential_rolls(start_str: str, count: int) -> List[str]:
    """
    Generates an ascending sequence of roll numbers preserving prefix and padding.

    Example:
        generate_sequential_rolls("2226128001", 3)
        -> ["2226128001", "2226128002", "2226128003"]
    """
    match = re.match(r"^(.*?)(\d+)$", start_str)
    if not match:
        return [start_str]

    prefix = match.group(1)
    numeric_part = match.group(2)
    start_number = int(numeric_part)
    pad_length = len(numeric_part)

    return [
        f"{prefix}{str(start_number + i).zfill(pad_length)}"
        for i in range(count)
    ]


def parse_student_groups(groups_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Transforms raw user input groups into three distinct sorted student slots:
    { "y1": [...], "y2": [...], "y3": [...] }

    Each student record: {"roll": "...", "year": 1}
    """
    results: Dict[str, List[Dict[str, Any]]] = {"y1": [], "y2": [], "y3": []}

    for group in groups_data:
        year_num = group.get("year", 3)
        raw_text = group.get("raw_list", "").strip()
        start_roll = group.get("start_roll", "").strip()
        count_str = str(group.get("count", "0")).strip()
        excluded = set(group.get("excluded_rolls", []))

        # Raw multiline text takes precedence over start_roll + count range
        rolls: List[str] = []
        if raw_text:
            rolls = [line.strip() for line in raw_text.splitlines() if line.strip()]
        elif start_roll and count_str.isdigit() and int(count_str) > 0:
            rolls = generate_sequential_rolls(start_roll, int(count_str))

        # Filter out exempted roll numbers if checkbox is active
        if group.get("exempt_checked", False):
            rolls = [r for r in rolls if r not in excluded]

        # Map the academic year to the target slot (y1, y2, y3)
        slot = YEARS.get(year_num, {}).get("slot", "y3")

        for roll in rolls:
            results[slot].append({"roll": roll, "year": year_num})

    # Deduplicate and sort roll numbers within each slot
    for slot in results:
        seen = set()
        unique_students = []
        for student in results[slot]:
            if student["roll"] not in seen:
                seen.add(student["roll"])
                unique_students.append(student)

        # Sort lexicographically by roll number
        unique_students.sort(key=lambda s: s["roll"])
        results[slot] = unique_students

    return results


def get_seat_number(row_num: int, desk_side: str, seat_index: int) -> int:
    """
    Calculates the 1-based vertical seat number (1-36).

    Layout breakdown:
      Seat Index 1 (Year 1): Left 1-6,  Right 7-12
      Seat Index 2 (Year 2): Left 13-18, Right 19-24
      Seat Index 3 (Year 3): Left 25-30, Right 31-36
    """
    row_offset = (row_num - 1) if desk_side == "left" else (6 + row_num - 1)
    slot_base = (seat_index - 1) * 12
    return 1 + slot_base + row_offset


def allocate_seating(
    students: Dict[str, List[Dict[str, Any]]],
    hall_names: List[str],
    capacity_per_year: int = 12,
) -> List[Dict[str, Any]]:
    """
    Distributes students across exam halls ensuring anti-cheating seat interleaving.

    Returns:
        List of hall configurations with row layouts and summary statistics.
    """
    y1_list = students["y1"]
    y2_list = students["y2"]
    y3_list = students["y3"]

    # Calculate total halls needed across all 3 years
    halls_needed_y1 = math.ceil(len(y1_list) / capacity_per_year) if y1_list else 0
    halls_needed_y2 = math.ceil(len(y2_list) / capacity_per_year) if y2_list else 0
    halls_needed_y3 = math.ceil(len(y3_list) / capacity_per_year) if y3_list else 0
    total_halls_needed = max(halls_needed_y1, halls_needed_y2, halls_needed_y3, 1)

    # Auto-extend hall names dynamically if required
    extended_names = list(hall_names)
    if len(extended_names) < total_halls_needed:
        last_name = extended_names[-1] if extended_names else "A0"
        match = re.search(r"\d+", last_name)
        prefix = last_name[0] if last_name else "A"
        last_num = int(match.group()) if match else 0

        for _ in range(total_halls_needed - len(extended_names)):
            last_num += 1
            extended_names.append(f"{prefix}{last_num}")

    rows_per_hall = math.ceil(capacity_per_year / 2)  # Default: 12 / 2 = 6 rows
    halls = []

    for h_index in range(total_halls_needed):
        hall_name = extended_names[h_index]

        # Slice current hall's cohort for each year
        start = h_index * capacity_per_year
        end = start + capacity_per_year
        hall_y1 = y1_list[start:end]
        hall_y2 = y2_list[start:end]
        hall_y3 = y3_list[start:end]

        rows = []
        for r in range(rows_per_hall):
            # Left desk: rows 1-6 (first half of hall cohort)
            left_y1 = hall_y1[r] if r < len(hall_y1) else None
            left_y2 = hall_y2[r] if r < len(hall_y2) else None
            left_y3 = hall_y3[r] if r < len(hall_y3) else None

            # Right desk: rows 1-6 (second half of hall cohort)
            ri = r + rows_per_hall
            right_y1 = hall_y1[ri] if ri < len(hall_y1) else None
            right_y2 = hall_y2[ri] if ri < len(hall_y2) else None
            right_y3 = hall_y3[ri] if ri < len(hall_y3) else None

            left_desk = [
                {
                    "roll": student["roll"],
                    "year": student["year"],
                    "seat_no": get_seat_number(r + 1, "left", idx),
                } if student else None
                for idx, student in enumerate([left_y1, left_y2, left_y3], start=1)
            ]

            right_desk = [
                {
                    "roll": student["roll"],
                    "year": student["year"],
                    "seat_no": get_seat_number(r + 1, "right", idx),
                } if student else None
                for idx, student in enumerate([right_y1, right_y2, right_y3], start=1)
            ]

            rows.append({
                "row_num": r + 1,
                "left_desk": left_desk,
                "right_desk": right_desk,
            })

        halls.append({
            "name": hall_name,
            "rows": rows,
            "stats": {
                "y1": len(hall_y1),
                "y2": len(hall_y2),
                "y3": len(hall_y3),
                "total": len(hall_y1) + len(hall_y2) + len(hall_y3),
            },
        })

    return halls


def build_master_list(halls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flattens hall allotments into a master notice-board list sorted by roll number.

    Returns:
        List of dicts: {"roll", "year", "hall", "location"}
    """
    records = []
    for hall in halls:
        for row in hall["rows"]:
            # Process Left Desk
            for idx, seat in enumerate(row["left_desk"]):
                if seat:
                    records.append({
                        "roll": seat["roll"],
                        "year": seat["year"],
                        "hall": hall["name"],
                        "location": (
                            f"Row {row['row_num']} - Left Bench - "
                            f"Seat {idx + 1} [Seat: {seat['seat_no']}]"
                        ),
                    })
            # Process Right Desk
            for idx, seat in enumerate(row["right_desk"]):
                if seat:
                    records.append({
                        "roll": seat["roll"],
                        "year": seat["year"],
                        "hall": hall["name"],
                        "location": (
                            f"Row {row['row_num']} - Right Bench - "
                            f"Seat {idx + 1} [Seat: {seat['seat_no']}]"
                        ),
                    })

    records.sort(key=lambda r: r["roll"])
    return records
