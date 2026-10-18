"""
export_service.py — Unified export service using the Strategy / Dispatcher pattern.

Centralizes:
  - File save dialog configurations (extensions, file types, default filenames)
  - Routing user choices to the corresponding Excel, CSV, or PDF exporter
  - Clean error handling and user notification messages
"""

from tkinter import filedialog
from typing import List, Dict, Any, Optional, Tuple

from app.excel_exporter import export_single_hall, export_all_halls, export_master_list
from app.csv_exporter import export_hall_csv, export_master_csv
from app.pdf_generator import export_hall_pdf, export_all_halls_pdf, export_master_pdf


EXPORT_OPTIONS: List[str] = [
    "Export Current Hall (Excel)",
    "Export All Halls (Excel)",
    "Export Master List (Excel)",
    "Export Current Hall (CSV)",
    "Export Master List (CSV)",
    "Export Current Hall (PDF)",
    "Export All Halls (PDF)",
    "Export Master List (PDF)",
]


class ExportService:
    """
    Handles export dispatching, file dialogs, and error catching for seating data.
    """

    @staticmethod
    def handle_export(
        choice: str,
        halls: List[Dict[str, Any]],
        current_hall: Optional[Dict[str, Any]],
        college_name: str,
        exam_title: str,
    ) -> Tuple[bool, str]:
        """
        Executes the requested export workflow based on the dropdown selection.

        Returns:
            Tuple[bool, str]: (is_success, status_message)
        """
        if not halls:
            return False, "Generate an allotment first before exporting."

        requires_current_hall = "Current Hall" in choice
        if requires_current_hall and not current_hall:
            return False, "Please select an active hall first."

        hall_name = current_hall["name"] if current_hall else ""

        # Dispatch table defining file extensions, dialog filters, and execution callables
        strategies = {
            "Export Current Hall (Excel)": {
                "ext": ".xlsx",
                "types": [("Excel files", "*.xlsx")],
                "filename": f"Seating_Plan_Hall_{hall_name}.xlsx",
                "action": lambda p: export_single_hall(current_hall, college_name, exam_title, p),
                "success_msg": f"Excel exported for Hall {hall_name}!",
            },
            "Export All Halls (Excel)": {
                "ext": ".xlsx",
                "types": [("Excel files", "*.xlsx")],
                "filename": "All_Halls_Seating_Plan.xlsx",
                "action": lambda p: export_all_halls(halls, college_name, exam_title, p),
                "success_msg": "All halls Excel exported successfully!",
            },
            "Export Master List (Excel)": {
                "ext": ".xlsx",
                "types": [("Excel files", "*.xlsx")],
                "filename": "Master_Seating_Allotment_List.xlsx",
                "action": lambda p: export_master_list(halls, college_name, exam_title, p),
                "success_msg": "Master list Excel exported successfully!",
            },
            "Export Current Hall (CSV)": {
                "ext": ".csv",
                "types": [("CSV files", "*.csv")],
                "filename": f"Seating_Plan_Hall_{hall_name}.csv",
                "action": lambda p: export_hall_csv(current_hall, p),
                "success_msg": f"CSV exported for Hall {hall_name}!",
            },
            "Export Master List (CSV)": {
                "ext": ".csv",
                "types": [("CSV files", "*.csv")],
                "filename": "Master_Seating_List.csv",
                "action": lambda p: export_master_csv(halls, p),
                "success_msg": "Master list CSV exported successfully!",
            },
            "Export Current Hall (PDF)": {
                "ext": ".pdf",
                "types": [("PDF files", "*.pdf")],
                "filename": f"Seating_Plan_Hall_{hall_name}.pdf",
                "action": lambda p: export_hall_pdf(current_hall, college_name, exam_title, p),
                "success_msg": f"PDF exported for Hall {hall_name}!",
            },
            "Export All Halls (PDF)": {
                "ext": ".pdf",
                "types": [("PDF files", "*.pdf")],
                "filename": "All_Halls_Seating_Plan.pdf",
                "action": lambda p: export_all_halls_pdf(halls, college_name, exam_title, p),
                "success_msg": "All halls PDF exported successfully!",
            },
            "Export Master List (PDF)": {
                "ext": ".pdf",
                "types": [("PDF files", "*.pdf")],
                "filename": "Master_Seating_List.pdf",
                "action": lambda p: export_master_pdf(halls, college_name, exam_title, p),
                "success_msg": "Master list PDF exported successfully!",
            },
        }

        config = strategies.get(choice)
        if not config:
            return False, f"Unknown export option: '{choice}'"

        try:
            target_path = filedialog.asksaveasfilename(
                defaultextension=config["ext"],
                filetypes=config["types"],
                initialfile=config["filename"],
            )

            # User closed or cancelled the file save dialog
            if not target_path:
                return False, ""

            config["action"](target_path)
            return True, config["success_msg"]

        except Exception as err:
            return False, f"Export failed: {str(err)}"
