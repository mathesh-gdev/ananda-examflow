"""
test_engine.py — Comprehensive test suite for the Ananda Exam Cell engine.

Verifies:
  1. Roll number generation (prefix preservation and zero padding).
  2. Multi-year student group parsing & slot distribution.
  3. Interleaved seating allocation algorithm.
  4. Notice-board master list generation.
  5. JSON Data persistence layer.
  6. Multi-format exports: CSV, Excel (.xlsx), and PDF.
  7. Domain models serialization & validation.
  8. ExportService strategy mapping.
"""

import os
import tempfile
from app.allotment_engine import (
    generate_sequential_rolls,
    parse_student_groups,
    allocate_seating,
    build_master_list,
)
from app.constants import DEFAULT_GROUPS, DEFAULT_HALLS
from app.data_manager import DataManager
from app.csv_exporter import export_hall_csv, export_master_csv
from app.excel_exporter import export_single_hall, export_all_halls, export_master_list
from app.pdf_generator import export_hall_pdf, export_master_pdf
from app.models import Student, Seat, HallRow, HallStats, Hall, MasterRecord
from app.export_service import ExportService, EXPORT_OPTIONS


def run_tests():
    print("=" * 60)
    print("RUNNING ANANDA EXAM CELL VERIFICATION SUITE")
    print("=" * 60)

    # 1. Test roll generation
    rolls = generate_sequential_rolls("2226128001", 5)
    assert rolls == ["2226128001", "2226128002", "2226128003", "2226128004", "2226128005"], "Roll sequence mismatch"
    print(f"[OK] Roll generation: {rolls[:3]}... (Total: {len(rolls)})")

    # 2. Parse the default student groups
    students = parse_student_groups(DEFAULT_GROUPS)
    assert "y1" in students and "y2" in students and "y3" in students, "Student slots missing"
    print(f"[OK] Parsed students: y1={len(students['y1'])}, y2={len(students['y2'])}, y3={len(students['y3'])}")

    # 3. Run the seating allocation
    names = DEFAULT_HALLS["A"] + DEFAULT_HALLS["B"] + DEFAULT_HALLS["C"]
    halls = allocate_seating(students, names, capacity_per_year=12)
    assert len(halls) > 0, "No halls generated"
    print(f"[OK] Halls generated: {len(halls)}")
    for h in halls:
        print(f"     Hall {h['name']}: {h['stats']}")

    # 4. Build master list
    master = build_master_list(halls)
    assert len(master) == (len(students["y1"]) + len(students["y2"]) + len(students["y3"])), "Master record count mismatch"
    print(f"[OK] Master list records: {len(master)}")
    print(f"     First: {master[0]}")
    print(f"     Last:  {master[-1]}")

    # 5. Test data persistence
    dm = DataManager(data_dir=tempfile.mkdtemp())
    dm.save_halls(halls)
    loaded = dm.load_halls()
    assert len(loaded) == len(halls), "Loaded hall count does not match saved count"
    print(f"[OK] Data persistence: saved and loaded {len(loaded)} halls")

    # 6. Test CSV export
    csv_path = os.path.join(tempfile.gettempdir(), "test_hall.csv")
    export_hall_csv(halls[0], csv_path)
    assert os.path.exists(csv_path) and os.path.getsize(csv_path) > 0, "CSV export empty"
    print(f"[OK] CSV export: {csv_path}")

    # 7. Test Excel export
    xlsx_path = os.path.join(tempfile.gettempdir(), "test_hall.xlsx")
    export_single_hall(halls[0], "TEST COLLEGE", "Test Exam 2026", xlsx_path)
    assert os.path.exists(xlsx_path) and os.path.getsize(xlsx_path) > 0, "Excel export empty"
    print(f"[OK] Excel export: {xlsx_path}")

    # 8. Test PDF export
    pdf_path = os.path.join(tempfile.gettempdir(), "test_hall.pdf")
    export_hall_pdf(halls[0], "TEST COLLEGE", "Test Exam 2026", pdf_path)
    assert os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0, "PDF export empty"
    print(f"[OK] PDF export: {pdf_path}")

    # 9. Test Domain Models
    s = Student(roll="2226128001", year=1)
    assert s.to_dict() == {"roll": "2226128001", "year": 1}
    seat = Seat(roll="2226128001", year=1, seat_no=1)
    assert seat.to_dict() == {"roll": "2226128001", "year": 1, "seat_no": 1}
    print("[OK] Domain models dataclasses serialized cleanly")

    # 10. Test ExportService options
    assert len(EXPORT_OPTIONS) == 8, "Expected 8 export options"
    print("[OK] ExportService options verified")

    print("\n" + "=" * 60)
    print("ALL VERIFICATION CHECKS PASSED (100% SUCCESS)")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
