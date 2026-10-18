# Ananda ExamFlow — Automated Examination Seating & Logistics Engine

> **A production-ready, anti-cheating automated seating allotment desktop application built with Python and CustomTkinter.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GUI: CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-indigo.svg)](https://github.com/TomSchimansky/CustomTkinter)

---

## 📌 Executive Summary

Examination cells in universities often face logistical bottlenecks when manually distributing hundreds of students into exam halls while preventing malpractice. **Ananda Exam Cell** automates this process using a **multi-year interleaved seating heuristic**. 

By interleaving students from different academic years across classroom desks, students sitting side-by-side or directly behind each other are taking different examination papers, mathematically eliminating peer cheating opportunities.

---

## 🏛️ System Architecture

The application is architected following the **Separation of Concerns (SoC)** principle, isolating domain logic, persistence, reporting, and graphical presentation:

```
┌────────────────────────────────────────────────────────┐
│                   Presentation Layer                   │
│   (CustomTkinter: AppWindow, AdminDashboard, UI Cards) │
└───────────────────────────┬────────────────────────────┘
                            │ Dispatches Events
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Application / Service Layer          │
│   (ExportService, DataManager, Event Handlers)         │
└───────────────┬────────────────────────┬───────────────┘
                │                        │
                ▼                        ▼
┌───────────────────────────────┐ ┌──────────────────────┐
│         Domain Logic          │ │     Export Layer     │
│ (allotment_engine, models.py) │ │ (openpyxl,reportlab) │
└───────────────────────────────┘ └──────────────────────┘
```

### Module Responsibilities:
- **`app/models.py`**: Strongly typed data models using Python standard dataclasses (`Student`, `Seat`, `Hall`, `HallRow`).
- **`app/allotment_engine.py`**: Pure, deterministic seating algorithm with zero GUI dependencies (100% unit-tested).
- **`app/export_service.py`**: Strategy-based file export orchestrator supporting Excel (.xlsx), PDF (.pdf), and CSV (.csv).
- **`app/data_manager.py`**: Local JSON persistence layer storing application configurations and active allotments.
- **`app/ui/`**: Modular, dark/light theme-aware CustomTkinter interface components (`AdminDashboard`, `GroupCard`, `HallVisualizer`, `MasterListView`, `ToastNotification`).

---

## 📐 The Anti-Cheating Seating Heuristic

Each exam hall accommodates up to **36 students** (configurable) structured as **6 rows**:

```
                         [ FRONT / BLACKBOARD ]
  
        LEFT DESK (3 Seats)                RIGHT DESK (3 Seats)
Row 1: [ Year 1 | Year 2 | Year 3 ]  AISLE  [ Year 1 | Year 2 | Year 3 ]
Row 2: [ Year 1 | Year 2 | Year 3 ]  AISLE  [ Year 1 | Year 2 | Year 3 ]
Row 3: [ Year 1 | Year 2 | Year 3 ]  AISLE  [ Year 1 | Year 2 | Year 3 ]
Row 4: [ Year 1 | Year 2 | Year 3 ]  AISLE  [ Year 1 | Year 2 | Year 3 ]
Row 5: [ Year 1 | Year 2 | Year 3 ]  AISLE  [ Year 1 | Year 2 | Year 3 ]
Row 6: [ Year 1 | Year 2 | Year 3 ]  AISLE  [ Year 1 | Year 2 | Year 3 ]
```

### Algorithmic Complexity:
- **Sorting Phase**: Lexicographical sorting of student roll numbers in each slot: $O(K \log K)$ where $K \le N$.
- **Distribution Phase**: Sequential slicing and desk allocation: $O(N)$ linear time.
- **Total Time Complexity**: $\mathcal{O}(N \log N)$ where $N$ is the total student count.
- **Space Complexity**: $\mathcal{O}(N)$ for memory allotment structures and JSON persistence.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/your-username/ananda-examcell.git
cd ananda-examcell
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python main.py
```

### 4. Run Automated Tests
```bash
python test_engine.py
```

---

## 📊 Key Features & Exports

| Format | Content | Engine | Primary Use Case |
|---|---|---|---|
| **Excel (`.xlsx`)** | Classroom Seating Matrix & Notice Board List | `openpyxl` | Staff administration & records |
| **PDF (`.pdf`)** | Formatted Color-Coded A4 Hall Charts | `reportlab` | Notice boards & hall door prints |
| **CSV (`.csv`)** | Flattened Student Allotment Records | Python `csv` | University ERP / Database import |

---

## 📖 In-Depth Learning & Interview Guide
For a line-by-line explanation of the entire codebase, Python concepts, and common interview questions, see:
👉 [**CODEBASE_STUDY_GUIDE.md**](CODEBASE_STUDY_GUIDE.md)
