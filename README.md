# Khan'z Academy Manager

## Overview

A complete offline Android management app for Khan'z Academy built with Python, Kivy, and KivyMD.  
All data is stored locally on-device using SQLite — no internet connection required.

---

## Features

- **PIN-based Admin Login** — Secure access with a 4-digit PIN (default: `1234`).
- **Student Management** — Register, search, edit, and delete students with class assignments.
- **Class / Course Management** — Add and manage classes with teacher name, monthly fee, and schedule.
- **Daily Attendance Tracking** — Mark each student as Present, Absent, or Late per class per date.  
  Re-marking a date replaces the existing record automatically.
- **Attendance Reports** — Monthly per-student summary showing present / absent / late counts and percentage.
- **Fee Management** — Bulk-generate pending fee records for a class/month, mark individual fees as paid, and track collected vs. pending totals.
- **PDF Voucher Generation** — Generate a formatted PDF fee voucher using fpdf2 and save it to device storage.
- **Dashboard** — Real-time stats: total students, total classes, revenue this month, pending fees, today's attendance percentage.
- **Change PIN** — Securely update the admin PIN from within the app.

---

## Tech Stack

| Component | Version |
|---|---|
| Python | 3 |
| Kivy | 2.1.0 |
| KivyMD | 1.1.1 |
| SQLite | Built-in (stdlib) |
| fpdf2 | Latest |
| Buildozer | Latest |

---

## Project Structure

```
khanz_academy/
├── main.py                          # App entry point
├── buildozer.spec                   # Android build configuration
├── libs/
│   ├── __init__.py
│   └── database.py                  # DatabaseManager — all SQLite operations
├── screens/
│   ├── __init__.py
│   ├── login_screen.py              # PIN-based login
│   ├── dashboard_screen.py          # Summary dashboard + navigation drawer
│   ├── student_list_screen.py       # List/search/delete students
│   ├── add_student_screen.py        # Add/edit student form
│   ├── class_list_screen.py         # List/delete classes
│   ├── add_class_screen.py          # Add/edit class form
│   ├── attendance_screen.py         # Mark daily attendance
│   ├── attendance_report_screen.py  # Monthly attendance summary
│   ├── fee_management_screen.py     # View/generate/pay fees
│   └── fee_voucher_screen.py        # Fee voucher + PDF download
└── assets/
    └── fonts/                       # (uses KivyMD built-in Roboto)
```

---

## Setup & Build

### 1. Install desktop dependencies

```bash
pip install kivy==2.1.0 kivymd==1.1.1 fpdf2 pillow
```

### 2. Run on desktop (for testing)

```bash
cd khanz_academy
python main.py
```

### 3. Install Buildozer (Linux/macOS)

```bash
pip install buildozer
```

### 4. Build debug APK

```bash
cd khanz_academy
buildozer android debug
```

The APK will appear in `bin/`.

### 5. Build release APK

```bash
buildozer android release
```

---

## Default Login

| Field | Value |
|---|---|
| PIN | `1234` |

The PIN can be changed from **Dashboard → Navigation Drawer → Change PIN**.

---

## Database

The SQLite database is created at:

- **Android:** `<app_internal_storage>/data/khanz_academy.db`  
- **Desktop:** `libs/data/khanz_academy.db`

Tables: `admin`, `classes`, `students`, `attendance`, `fee_records`

---

## PDF Vouchers

Generated PDFs are saved to:

- **Android:** `<app_internal_storage>/vouchers/voucher_<id>.pdf`
- **Desktop:** `~/vouchers/voucher_<id>.pdf`

---

## Buildozer Notes

- `title = Khanz Academy` — **no apostrophe** to avoid XML parsing failure during APK build.
- `requirements` does **not** include `sqlite3` — it is part of the Python standard library.
- `android.permissions` includes `READ_EXTERNAL_STORAGE` and `WRITE_EXTERNAL_STORAGE` for PDF saving.

---

## Navigation Flow

```
Login → Dashboard
         ├── Students → Student List → Add/Edit Student
         ├── Classes  → Class List  → Add/Edit Class
         ├── Attendance → Mark Attendance
         │              └── Attendance Report
         ├── Fee Management → Fee List
         │                   ├── Mark Paid
         │                   └── Fee Voucher → Download PDF
         └── Change PIN (dialog)
```

---

## License

Private / Proprietary — Khan'z Academy internal use.
