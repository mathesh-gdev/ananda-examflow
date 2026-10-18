"""
pdf_generator.py — Generate PDF seating plans using reportlab.

Replaces the jsPDF-based exports from the original web app.
Generates print-ready PDF documents with:
  1. Single hall seating chart (A4 landscape)
  2. All halls combined (one page per hall)
  3. Master allotment list (A4 portrait table)
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.constants import YEARS
from app.allotment_engine import build_master_list


# ---------------------------------------------------------------------------
# COLOR CONSTANTS FOR PDF
# ---------------------------------------------------------------------------
COLOR_PRIMARY = HexColor("#4f46e5")
COLOR_YEAR_1  = HexColor("#3b82f6")
COLOR_YEAR_2  = HexColor("#10b981")
COLOR_YEAR_3  = HexColor("#f59e0b")
COLOR_HEADER  = HexColor("#e2e8f0")
COLOR_BORDER  = HexColor("#cbd5e1")


# ---------------------------------------------------------------------------
# SINGLE HALL PDF
# ---------------------------------------------------------------------------

def export_hall_pdf(
    hall: dict,
    college_name: str,
    exam_title: str,
    filepath: str,
) -> None:
    """
    Export a single hall's seating layout to a PDF file (A4 landscape).
    Shows a table grid with color-coded cells for each year.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    elements = []

    # Title section
    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    title_style.fontSize = 14

    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = TA_CENTER
    subtitle_style.fontSize = 11

    elements.append(Paragraph(college_name.upper(), title_style))
    elements.append(Paragraph(exam_title, subtitle_style))
    elements.append(Paragraph(f"SEATING PLAN: HALL {hall['name']}", subtitle_style))
    elements.append(Spacer(1, 8 * mm))

    # Build the seating table data
    # Header row: Left Desk labels | Aisle | Right Desk labels
    header_row = [
        "Seat 1\n(Y1)", "Seat 2\n(Y2)", "Seat 3\n(Y3)",
        "Row",
        "Seat 4\n(Y1)", "Seat 5\n(Y2)", "Seat 6\n(Y3)",
    ]
    table_data = [header_row]

    for row in hall["rows"]:
        data_row = []
        # Left desk
        for seat in row["left_desk"]:
            if seat:
                data_row.append(f"{seat['roll']}\nS:{seat['seat_no']}")
            else:
                data_row.append("-")
        # Row number
        data_row.append(str(row["row_num"]))
        # Right desk
        for seat in row["right_desk"]:
            if seat:
                data_row.append(f"{seat['roll']}\nS:{seat['seat_no']}")
            else:
                data_row.append("-")
        table_data.append(data_row)

    # Create the table with styling
    col_widths = [75, 75, 75, 30, 75, 75, 75]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Build style commands
    style_commands = [
        # Global
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("GRID",        (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("BACKGROUND",  (0, 0), (-1, 0),  COLOR_HEADER),
        # Row number column
        ("BACKGROUND",  (3, 1), (3, -1),  HexColor("#f1f5f9")),
        ("FONTNAME",    (3, 1), (3, -1),  "Helvetica-Bold"),
    ]

    # Color-code seats by year
    for row_idx in range(1, len(table_data)):
        row_data = hall["rows"][row_idx - 1]
        # Left desk seats (columns 0, 1, 2)
        for col, seat in enumerate(row_data["left_desk"]):
            if seat:
                year = seat["year"]
                if year in (1, 4):
                    bg = HexColor("#dbeafe")
                elif year in (2, 5):
                    bg = HexColor("#d1fae5")
                else:
                    bg = HexColor("#fef3c7")
                style_commands.append(("BACKGROUND", (col, row_idx), (col, row_idx), bg))
        # Right desk seats (columns 4, 5, 6)
        for col_offset, seat in enumerate(row_data["right_desk"]):
            col = 4 + col_offset
            if seat:
                year = seat["year"]
                if year in (1, 4):
                    bg = HexColor("#dbeafe")
                elif year in (2, 5):
                    bg = HexColor("#d1fae5")
                else:
                    bg = HexColor("#fef3c7")
                style_commands.append(("BACKGROUND", (col, row_idx), (col, row_idx), bg))

    table.setStyle(TableStyle(style_commands))
    elements.append(table)

    # Legend
    elements.append(Spacer(1, 5 * mm))
    legend_style = styles["Normal"]
    legend_style.fontSize = 8
    legend_text = (
        '<font color="#3b82f6">■</font> Year 1 (Blue) &nbsp;&nbsp; '
        '<font color="#10b981">■</font> Year 2 (Green) &nbsp;&nbsp; '
        '<font color="#f59e0b">■</font> Year 3 (Amber) &nbsp;&nbsp; '
        '- = Empty Seat'
    )
    elements.append(Paragraph(legend_text, legend_style))

    doc.build(elements)


# ---------------------------------------------------------------------------
# ALL HALLS PDF
# ---------------------------------------------------------------------------

def export_all_halls_pdf(
    halls: list[dict],
    college_name: str,
    exam_title: str,
    filepath: str,
) -> None:
    """
    Export all halls into one PDF, each hall on its own page.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    elements = []

    for i, hall in enumerate(halls):
        title_style = styles["Title"]
        title_style.alignment = TA_CENTER
        title_style.fontSize = 14

        subtitle_style = styles["Heading2"]
        subtitle_style.alignment = TA_CENTER
        subtitle_style.fontSize = 11

        elements.append(Paragraph(college_name.upper(), title_style))
        elements.append(Paragraph(exam_title, subtitle_style))
        elements.append(Paragraph(f"SEATING PLAN: HALL {hall['name']}", subtitle_style))
        elements.append(Spacer(1, 6 * mm))

        # Build table
        header_row = [
            "Seat 1\n(Y1)", "Seat 2\n(Y2)", "Seat 3\n(Y3)",
            "Row",
            "Seat 4\n(Y1)", "Seat 5\n(Y2)", "Seat 6\n(Y3)",
        ]
        table_data = [header_row]

        for row in hall["rows"]:
            data_row = []
            for seat in row["left_desk"]:
                data_row.append(f"{seat['roll']}\nS:{seat['seat_no']}" if seat else "-")
            data_row.append(str(row["row_num"]))
            for seat in row["right_desk"]:
                data_row.append(f"{seat['roll']}\nS:{seat['seat_no']}" if seat else "-")
            table_data.append(data_row)

        col_widths = [75, 75, 75, 30, 75, 75, 75]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        style_commands = [
            ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME",   (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("GRID",       (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("BACKGROUND", (0, 0), (-1, 0),  COLOR_HEADER),
            ("BACKGROUND", (3, 1), (3, -1),  HexColor("#f1f5f9")),
        ]

        for row_idx in range(1, len(table_data)):
            row_obj = hall["rows"][row_idx - 1]
            for col, seat in enumerate(row_obj["left_desk"]):
                if seat:
                    year = seat["year"]
                    bg = HexColor("#dbeafe") if year in (1, 4) else (
                        HexColor("#d1fae5") if year in (2, 5) else HexColor("#fef3c7"))
                    style_commands.append(("BACKGROUND", (col, row_idx), (col, row_idx), bg))
            for col_offset, seat in enumerate(row_obj["right_desk"]):
                col = 4 + col_offset
                if seat:
                    year = seat["year"]
                    bg = HexColor("#dbeafe") if year in (1, 4) else (
                        HexColor("#d1fae5") if year in (2, 5) else HexColor("#fef3c7"))
                    style_commands.append(("BACKGROUND", (col, row_idx), (col, row_idx), bg))

        table.setStyle(TableStyle(style_commands))
        elements.append(table)

        # Page break between halls (but not after the last one)
        if i < len(halls) - 1:
            elements.append(PageBreak())

    doc.build(elements)


# ---------------------------------------------------------------------------
# MASTER LIST PDF
# ---------------------------------------------------------------------------

def export_master_pdf(
    halls: list[dict],
    college_name: str,
    exam_title: str,
    filepath: str,
) -> None:
    """
    Export the sorted master allotment list as a portrait A4 PDF table.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    title_style.fontSize = 13

    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = TA_CENTER
    subtitle_style.fontSize = 10

    elements.append(Paragraph(college_name.upper(), title_style))
    elements.append(Paragraph(exam_title, subtitle_style))
    elements.append(Paragraph("MASTER SEATING ALLOTMENT LIST", subtitle_style))
    elements.append(Spacer(1, 6 * mm))

    # Build table
    records = build_master_list(halls)
    header = ["S.No", "Register Number", "Academic Year", "Hall", "Seat Location"]
    table_data = [header]

    for i, record in enumerate(records, start=1):
        year_label = YEARS.get(record["year"], {}).get("label", f"Year {record['year']}")
        table_data.append([
            str(i),
            record["roll"],
            year_label,
            record["hall"],
            record["location"],
        ])

    col_widths = [30, 95, 80, 40, 140]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    table.setStyle(TableStyle([
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  9),
        ("FONTSIZE",    (0, 1), (-1, -1), 7.5),
        ("BACKGROUND",  (0, 0), (-1, 0),  COLOR_HEADER),
        ("GRID",        (0, 0), (-1, -1), 0.4, COLOR_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#f8fafc")]),
    ]))

    elements.append(table)
    doc.build(elements)
