# File: libs/database.py
"""
DatabaseManager — All SQLite operations for Khan'z Academy Manager.
Every method wraps its logic in try-except and closes the connection in finally.
"""

import os
import sqlite3
from pathlib import Path
from datetime import date, datetime


# ---------------------------------------------------------------------------
# Utility: safe, writable DB path on both desktop and Android
# ---------------------------------------------------------------------------

def get_db_path():
    """Return a writable database path that works on both desktop and Android."""
    try:
        from android.storage import app_storage_path  # noqa — Android only
        base = app_storage_path()
    except ImportError:
        # Desktop / CI fallback: place the DB next to this file
        base = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base, 'data')
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(db_dir, 'khanz_academy.db')


# ---------------------------------------------------------------------------
# DatabaseManager class
# ---------------------------------------------------------------------------

class DatabaseManager:
    """
    Manages all SQLite interactions for the app.
    Each public method opens a fresh connection, performs its work,
    commits if needed, and closes the connection in a finally block.
    """

    def __init__(self):
        self.db_path = get_db_path()
        self._create_tables()
        self._seed_admin()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_connection(self):
        """Open and return a sqlite3 connection with Row factory set."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_tables(self):
        """Create all tables on first launch if they do not exist."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS admin (
                    id  INTEGER PRIMARY KEY AUTOINCREMENT,
                    pin TEXT    NOT NULL DEFAULT '1234'
                );

                CREATE TABLE IF NOT EXISTS classes (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name   TEXT    NOT NULL,
                    teacher_name TEXT    NOT NULL,
                    monthly_fee  REAL    NOT NULL DEFAULT 0.0,
                    schedule     TEXT    DEFAULT '',
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS students (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name       TEXT    NOT NULL,
                    phone           TEXT    DEFAULT '',
                    class_id        INTEGER,
                    enrollment_date TEXT    DEFAULT (date('now')),
                    is_active       INTEGER DEFAULT 1,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS attendance (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    class_id   INTEGER NOT NULL,
                    date       TEXT    NOT NULL,
                    status     TEXT    NOT NULL CHECK(status IN ('Present','Absent','Late')),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (class_id)   REFERENCES classes(id)  ON DELETE CASCADE,
                    UNIQUE(student_id, class_id, date)
                );

                CREATE TABLE IF NOT EXISTS fee_records (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id  INTEGER NOT NULL,
                    class_id    INTEGER NOT NULL,
                    amount      REAL    NOT NULL,
                    month       TEXT    NOT NULL,
                    year        INTEGER NOT NULL,
                    status      TEXT    NOT NULL DEFAULT 'Pending'
                                        CHECK(status IN ('Paid','Pending')),
                    paid_date   TEXT,
                    voucher_path TEXT,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (class_id)   REFERENCES classes(id)  ON DELETE CASCADE
                );
            """)
            conn.commit()
        except Exception as e:
            print(f"[DB] _create_tables error: {e}")
        finally:
            if conn:
                conn.close()

    def _seed_admin(self):
        """Insert a default admin row with PIN '1234' if none exists."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM admin")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("INSERT INTO admin (pin) VALUES (?)", ("1234",))
                conn.commit()
        except Exception as e:
            print(f"[DB] _seed_admin error: {e}")
        finally:
            if conn:
                conn.close()

    # ==================================================================
    # ADMIN methods
    # ==================================================================

    def verify_pin(self, pin: str) -> bool:
        """Return True if the given PIN matches the stored admin PIN."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT pin FROM admin LIMIT 1")
            row = cursor.fetchone()
            if row is None:
                return False
            return str(row["pin"]) == str(pin).strip()
        except Exception as e:
            print(f"[DB] verify_pin error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def update_pin(self, old_pin: str, new_pin: str) -> bool:
        """
        Update the admin PIN only if the old_pin matches the current PIN.
        Returns True on success, False otherwise.
        """
        conn = None
        try:
            if not self.verify_pin(old_pin):
                return False
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE admin SET pin = ? WHERE id = (SELECT id FROM admin LIMIT 1)",
                           (str(new_pin).strip(),))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] update_pin error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # ==================================================================
    # CLASSES methods
    # ==================================================================

    def add_class(self, class_name: str, teacher_name: str,
                  monthly_fee: float, schedule: str) -> int:
        """
        Insert a new class record.
        Returns the new row id, or 0 on failure.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO classes (class_name, teacher_name, monthly_fee, schedule) "
                "VALUES (?, ?, ?, ?)",
                (class_name.strip(), teacher_name.strip(),
                 float(monthly_fee), schedule.strip())
            )
            conn.commit()
            return cursor.lastrowid or 0
        except Exception as e:
            print(f"[DB] add_class error: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def get_all_classes(self) -> list:
        """Return a list of all class records as dicts."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, class_name, teacher_name, monthly_fee, schedule, created_at "
                "FROM classes ORDER BY class_name ASC"
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[DB] get_all_classes error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_class_by_id(self, class_id: int) -> dict:
        """Return a single class record as a dict, or empty dict on failure."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, class_name, teacher_name, monthly_fee, schedule, created_at "
                "FROM classes WHERE id = ?",
                (int(class_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            print(f"[DB] get_class_by_id error: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def update_class(self, class_id: int, class_name: str, teacher_name: str,
                     monthly_fee: float, schedule: str) -> bool:
        """Update an existing class record. Returns True on success."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE classes SET class_name=?, teacher_name=?, monthly_fee=?, schedule=? "
                "WHERE id=?",
                (class_name.strip(), teacher_name.strip(),
                 float(monthly_fee), schedule.strip(), int(class_id))
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] update_class error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def delete_class(self, class_id: int) -> bool:
        """Delete a class by id. Returns True on success."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM classes WHERE id=?", (int(class_id),))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] delete_class error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # ==================================================================
    # STUDENTS methods
    # ==================================================================

    def add_student(self, full_name: str, phone: str, class_id) -> int:
        """
        Insert a new student record.
        Returns the new row id, or 0 on failure.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cid = int(class_id) if class_id else None
            cursor.execute(
                "INSERT INTO students (full_name, phone, class_id) VALUES (?, ?, ?)",
                (full_name.strip(), str(phone).strip(), cid)
            )
            conn.commit()
            return cursor.lastrowid or 0
        except Exception as e:
            print(f"[DB] add_student error: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def get_all_students(self) -> list:
        """Return all active students joined with their class name."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.full_name, s.phone, s.class_id,
                       s.enrollment_date, s.is_active, s.created_at,
                       COALESCE(c.class_name, 'No Class') AS class_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                WHERE s.is_active = 1
                ORDER BY s.full_name ASC
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[DB] get_all_students error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_students_by_class(self, class_id: int) -> list:
        """Return all active students belonging to a specific class."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.full_name, s.phone, s.class_id,
                       s.enrollment_date, s.is_active,
                       COALESCE(c.class_name, 'No Class') AS class_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                WHERE s.is_active = 1 AND s.class_id = ?
                ORDER BY s.full_name ASC
            """, (int(class_id),))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[DB] get_students_by_class error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def search_students(self, query: str) -> list:
        """
        Search students by full_name or phone using a LIKE query.
        Returns matching active students with class name.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            pattern = f"%{query.strip()}%"
            cursor.execute("""
                SELECT s.id, s.full_name, s.phone, s.class_id,
                       s.enrollment_date, s.is_active,
                       COALESCE(c.class_name, 'No Class') AS class_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                WHERE s.is_active = 1
                  AND (s.full_name LIKE ? OR s.phone LIKE ?)
                ORDER BY s.full_name ASC
            """, (pattern, pattern))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[DB] search_students error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_student_by_id(self, student_id: int) -> dict:
        """Return a single student record as a dict, or empty dict on failure."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.full_name, s.phone, s.class_id,
                       s.enrollment_date, s.is_active,
                       COALESCE(c.class_name, 'No Class') AS class_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                WHERE s.id = ?
            """, (int(student_id),))
            row = cursor.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            print(f"[DB] get_student_by_id error: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def update_student(self, student_id: int, full_name: str,
                       phone: str, class_id) -> bool:
        """Update an existing student record. Returns True on success."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cid = int(class_id) if class_id else None
            cursor.execute(
                "UPDATE students SET full_name=?, phone=?, class_id=? WHERE id=?",
                (full_name.strip(), str(phone).strip(), cid, int(student_id))
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] update_student error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def delete_student(self, student_id: int) -> bool:
        """Soft-delete a student by setting is_active=0. Returns True on success."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET is_active=0 WHERE id=?", (int(student_id),)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] delete_student error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # ==================================================================
    # ATTENDANCE methods
    # ==================================================================

    def mark_attendance(self, student_id: int, class_id: int,
                        att_date: str, status: str) -> bool:
        """
        Insert or replace an attendance record (handles re-marking).
        status must be one of: 'Present', 'Absent', 'Late'.
        Returns True on success.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO attendance (student_id, class_id, date, status)
                VALUES (?, ?, ?, ?)
            """, (int(student_id), int(class_id), str(att_date), str(status)))
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB] mark_attendance error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_attendance_by_class_date(self, class_id: int, att_date: str) -> list:
        """
        Return attendance records for all students in a class on a given date.
        Includes student name for display.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.student_id, a.class_id, a.date, a.status,
                       s.full_name
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE a.class_id = ? AND a.date = ?
                ORDER BY s.full_name ASC
            """, (int(class_id), str(att_date)))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[DB] get_attendance_by_class_date error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_attendance_report(self, class_id: int, month: str, year: int) -> list:
        """
        Return a per-student attendance summary for a given class/month/year.
        Each dict contains: student_id, full_name, present, absent, late, total, pct.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Build date prefix for LIKE matching (e.g. '2024-03-%')
            month_num = month if len(str(month)) == 2 else str(month).zfill(2)
            date_prefix = f"{int(year)}-{month_num}-%"
            cursor.execute("""
                SELECT s.id AS student_id, s.full_name,
                       SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present,
                       SUM(CASE WHEN a.status='Absent'  THEN 1 ELSE 0 END) AS absent,
                       SUM(CASE WHEN a.status='Late'    THEN 1 ELSE 0 END) AS late,
                       COUNT(a.id) AS total
                FROM students s
                LEFT JOIN attendance a
                       ON a.student_id = s.id
                      AND a.class_id   = ?
                      AND a.date LIKE ?
                WHERE s.class_id = ? AND s.is_active = 1
                GROUP BY s.id
                ORDER BY s.full_name ASC
            """, (int(class_id), date_prefix, int(class_id)))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                r = dict(row)
                total = r.get("total", 0) or 0
                present = r.get("present", 0) or 0
                r["pct"] = round((present / total * 100), 1) if total > 0 else 0.0
                result.append(r)
            return result
        except Exception as e:
            print(f"[DB] get_attendance_report error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_today_attendance_summary(self) -> dict:
        """
        Return a summary dict for today's attendance across all classes:
        {total, present, absent, late}
        """
        conn = None
        try:
            today_str = date.today().isoformat()
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)                                           AS total,
                       SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present,
                       SUM(CASE WHEN status='Absent'  THEN 1 ELSE 0 END) AS absent,
                       SUM(CASE WHEN status='Late'    THEN 1 ELSE 0 END) AS late
                FROM attendance
                WHERE date = ?
            """, (today_str,))
            row = cursor.fetchone()
            if row:
                return {
                    "total":   row["total"]   or 0,
                    "present": row["present"] or 0,
                    "absent":  row["absent"]  or 0,
                    "late":    row["late"]    or 0,
                }
            return {"total": 0, "present": 0, "absent": 0, "late": 0}
        except Exception as e:
            print(f"[DB] get_today_attendance_summary error: {e}")
            return {"total": 0, "present": 0, "absent": 0, "late": 0}
        finally:
            if conn:
                conn.close()

    # ==================================================================
    # FEES methods
    # ==================================================================

    def generate_monthly_fees(self, class_id: int, month: str, year: int) -> int:
        """
        Bulk-create Pending fee records for all active students in a class
        for the given month/year.  Skips students that already have a record
        for that month/year.
        Returns the number of new records inserted.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get class monthly fee
            cursor.execute(
                "SELECT monthly_fee FROM classes WHERE id=?", (int(class_id),)
            )
            cls_row = cursor.fetchone()
            if not cls_row:
                return 0
            monthly_fee = cls_row["monthly_fee"]

            # Get active students in this class
            cursor.execute(
                "SELECT id FROM students WHERE class_id=? AND is_active=1",
                (int(class_id),)
            )
            students = cursor.fetchall()

            inserted = 0
            for stu in students:
                sid = stu["id"]
                # Check if already exists
                cursor.execute(
                    "SELECT id FROM fee_records WHERE student_id=? AND class_id=? "
                    "AND month=? AND year=?",
                    (sid, int(class_id), str(month), int(year))
                )
                existing = cursor.fetchone()
                if not existing:
                    cursor.execute(
                        "INSERT INTO fee_records (student_id, class_id, amount, month, year, status) "
                        "VALUES (?, ?, ?, ?, ?, 'Pending')",
                        (sid, int(class_id), float(monthly_fee), str(month), int(year))
                    )
                    inserted += 1

            conn.commit()
            return inserted
        except Exception as e:
            print(f"[DB] generate_monthly_fees error: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def get_fee_records(self, class_id: int, month: str, year: int) -> list:
        """
        Return fee records for a class/month/year with student names.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fr.id, fr.student_id, fr.class_id,
                       fr.amount, fr.month, fr.year,
                       fr.status, fr.paid_date, fr.voucher_path,
                       s.full_name,
                       COALESCE(c.class_name, 'No Class') AS class_name
                FROM fee_records fr
                JOIN students s ON fr.student_id = s.id
                LEFT JOIN classes c ON fr.class_id = c.id
                WHERE fr.class_id=? AND fr.month=? AND fr.year=?
                ORDER BY s.full_name ASC
            """, (int(class_id), str(month), int(year)))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[DB] get_fee_records error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_fee_record_by_id(self, fee_id: int) -> dict:
        """Return a single fee record with student and class details."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fr.id, fr.student_id, fr.class_id,
                       fr.amount, fr.month, fr.year,
                       fr.status, fr.paid_date, fr.voucher_path,
                       s.full_name,
                       COALESCE(c.class_name, 'No Class') AS class_name
                FROM fee_records fr
                JOIN students s ON fr.student_id = s.id
                LEFT JOIN classes c ON fr.class_id = c.id
                WHERE fr.id=?
            """, (int(fee_id),))
            row = cursor.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            print(f"[DB] get_fee_record_by_id error: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def mark_fee_paid(self, fee_id: int) -> bool:
        """
        Mark a fee record as Paid and set paid_date to today.
        Returns True on success.
        """
        conn = None
        try:
            today_str = date.today().isoformat()
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE fee_records SET status='Paid', paid_date=? WHERE id=?",
                (today_str, int(fee_id))
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] mark_fee_paid error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_fee_summary(self) -> dict:
        """
        Return overall fee summary:
        {total_collected_this_month, total_pending}
        """
        conn = None
        try:
            now = datetime.now()
            current_month = now.strftime("%B")
            current_year = now.year
            conn = self._get_connection()
            cursor = conn.cursor()

            # Total collected this month
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0.0) AS collected
                FROM fee_records
                WHERE status='Paid' AND month=? AND year=?
            """, (current_month, current_year))
            row = cursor.fetchone()
            collected = row["collected"] if row else 0.0

            # Total pending (all time)
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0.0) AS pending
                FROM fee_records
                WHERE status='Pending'
            """)
            row2 = cursor.fetchone()
            pending = row2["pending"] if row2 else 0.0

            return {
                "total_collected_this_month": collected,
                "total_pending": pending
            }
        except Exception as e:
            print(f"[DB] get_fee_summary error: {e}")
            return {"total_collected_this_month": 0.0, "total_pending": 0.0}
        finally:
            if conn:
                conn.close()

    def update_voucher_path(self, fee_id: int, path: str) -> bool:
        """Update the voucher_path field for a fee record after PDF is generated."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE fee_records SET voucher_path=? WHERE id=?",
                (str(path), int(fee_id))
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] update_voucher_path error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # ==================================================================
    # DASHBOARD stats
    # ==================================================================

    def get_dashboard_stats(self) -> dict:
        """
        Return aggregate stats for the dashboard:
        {total_students, total_classes, revenue_this_month,
         pending_fees, attendance_today_pct}
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.now()
            current_month = now.strftime("%B")
            current_year = now.year
            today_str = date.today().isoformat()

            # Total active students
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM students WHERE is_active=1"
            )
            total_students = cursor.fetchone()["cnt"] or 0

            # Total classes
            cursor.execute("SELECT COUNT(*) AS cnt FROM classes")
            total_classes = cursor.fetchone()["cnt"] or 0

            # Revenue this month (sum of Paid fees)
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0.0) AS rev
                FROM fee_records
                WHERE status='Paid' AND month=? AND year=?
            """, (current_month, current_year))
            revenue = cursor.fetchone()["rev"] or 0.0

            # Total pending fees
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0.0) AS pend
                FROM fee_records WHERE status='Pending'
            """)
            pending = cursor.fetchone()["pend"] or 0.0

            # Today's attendance percentage
            cursor.execute("""
                SELECT COUNT(*)                                           AS total,
                       SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present
                FROM attendance WHERE date=?
            """, (today_str,))
            att_row = cursor.fetchone()
            att_total = att_row["total"] or 0
            att_present = att_row["present"] or 0
            att_pct = round((att_present / att_total * 100), 1) if att_total > 0 else 0.0

            return {
                "total_students": total_students,
                "total_classes": total_classes,
                "revenue_this_month": revenue,
                "pending_fees": pending,
                "attendance_today_pct": att_pct,
            }
        except Exception as e:
            print(f"[DB] get_dashboard_stats error: {e}")
            return {
                "total_students": 0,
                "total_classes": 0,
                "revenue_this_month": 0.0,
                "pending_fees": 0.0,
                "attendance_today_pct": 0.0,
            }
        finally:
            if conn:
                conn.close()
