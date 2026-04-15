# File: screens/attendance_screen.py
"""
Attendance Screen — Mark attendance for a class on a specific date.
All KV layout is embedded inline via Builder.load_string().
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from datetime import date
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import TwoLineListItem, MDList
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDIcon

Builder.load_string("""
<AttendanceScreen>:
    name: "attendance"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 245/255, 245/255, 245/255, 1

        MDTopAppBar:
            title: "Mark Attendance"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["chart-bar", lambda x: root.go_report()]]
            elevation: 2

        ScrollView:

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "12dp"
                spacing: "12dp"

                # ── Selector Card ────────────────────────────────────────
                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    radius: [16, 16, 16, 16]
                    elevation: 1.5
                    padding: "16dp"
                    spacing: "12dp"
                    md_bg_color: 1, 1, 1, 1

                    MDLabel:
                        text: "Select Class & Date"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 63/255, 81/255, 181/255, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(4)

                    MDTextField:
                        id: class_display_field
                        hint_text: "Tap to select a class"
                        icon_left: "google-classroom"
                        mode: "rectangle"
                        readonly: True
                        size_hint_y: None
                        height: "52dp"
                        on_focus: if self.focus: root.show_class_picker()

                    MDRaisedButton:
                        text: "SELECT CLASS"
                        size_hint_x: 1
                        size_hint_y: None
                        height: "44dp"
                        md_bg_color: 38/255, 166/255, 154/255, 1
                        on_release: root.show_class_picker()

                    MDTextField:
                        id: date_display_field
                        hint_text: "Date"
                        icon_left: "calendar"
                        mode: "rectangle"
                        readonly: True
                        size_hint_y: None
                        height: "52dp"
                        on_focus: if self.focus: root.show_date_picker()

                    MDRaisedButton:
                        text: "SELECT DATE"
                        size_hint_x: 1
                        size_hint_y: None
                        height: "44dp"
                        md_bg_color: 63/255, 81/255, 181/255, 1
                        on_release: root.show_date_picker()

                # ── Student Attendance List ──────────────────────────────
                MDCard:
                    id: attendance_card
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    radius: [16, 16, 16, 16]
                    elevation: 1.5
                    padding: "16dp"
                    spacing: "8dp"
                    md_bg_color: 1, 1, 1, 1

                    MDLabel:
                        id: attendance_title_lbl
                        text: "Students"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 63/255, 81/255, 181/255, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(4)

                    MDBoxLayout:
                        id: student_rows
                        orientation: "vertical"
                        adaptive_height: True
                        spacing: "8dp"

                # ── Save Button ──────────────────────────────────────────
                MDRaisedButton:
                    id: save_attendance_btn
                    text: "SAVE ATTENDANCE"
                    size_hint_x: 1
                    size_hint_y: None
                    height: "52dp"
                    md_bg_color: 63/255, 81/255, 181/255, 1
                    on_release: root.save_attendance()

                Widget:
                    size_hint_y: None
                    height: "16dp"
""")


class AttendanceScreen(MDScreen):
    """Screen for marking daily attendance for a class."""

    name = "attendance"

    # Internal state
    _selected_class_id = None
    _selected_class_name = ""
    _selected_date = None        # datetime.date object
    _student_status = {}         # {student_id: status_str}
    _students = []               # list of student dicts

    _class_picker_dialog = None
    _date_picker = None
    _error_dialog = None

    def on_pre_enter(self):
        """Reset form state each time the screen is entered."""
        self.refresh_data()

    def refresh_data(self):
        """Reset selections and clear student attendance rows."""
        try:
            self._selected_class_id = None
            self._selected_class_name = ""
            self._selected_date = date.today()
            self._student_status = {}
            self._students = []

            self.ids.class_display_field.text = ""
            self.ids.date_display_field.text = self._selected_date.isoformat()
            self.ids.student_rows.clear_widgets()
            self.ids.attendance_title_lbl.text = "Select a class to load students"
        except Exception as e:
            print(f"[AttendanceScreen] refresh_data error: {e}")

    # ------------------------------------------------------------------
    # Class picker
    # ------------------------------------------------------------------

    def show_class_picker(self):
        """Show a dialog to select a class."""
        try:
            if self._class_picker_dialog:
                self._class_picker_dialog.dismiss()

            app = App.get_running_app()
            classes = app.db.get_all_classes()

            if not classes:
                self._show_error_dialog(
                    "No Classes", "No classes found. Please add a class first."
                )
                return

            list_widget = MDList()
            from kivy.uix.scrollview import ScrollView as KVScrollView
            scroll = KVScrollView(
                size_hint_y=None,
                height=min(dp(280), len(classes) * dp(60))
            )

            for cls in classes:
                item = TwoLineListItem(
                    text=cls["class_name"],
                    secondary_text=f"Teacher: {cls['teacher_name']}",
                )
                cid = cls["id"]
                cname = cls["class_name"]
                item.bind(on_release=lambda x, c_id=cid, c_name=cname:
                          self._select_class(c_id, c_name))
                list_widget.add_widget(item)

            scroll.add_widget(list_widget)

            self._class_picker_dialog = MDDialog(
                title="Select Class",
                type="custom",
                content_cls=scroll,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self._class_picker_dialog.dismiss()
                    )
                ]
            )
            self._class_picker_dialog.open()
        except Exception as e:
            self._show_error_dialog("Error", f"Could not open class picker: {str(e)}")

    def _select_class(self, class_id: int, class_name: str):
        """Handle class selection and load students."""
        try:
            self._selected_class_id = class_id
            self._selected_class_name = class_name
            self.ids.class_display_field.text = class_name
            if self._class_picker_dialog:
                self._class_picker_dialog.dismiss()
            self._load_students_for_attendance()
        except Exception as e:
            self._show_error_dialog("Error", str(e))

    # ------------------------------------------------------------------
    # Date picker
    # ------------------------------------------------------------------

    def show_date_picker(self):
        """Open the KivyMD date picker dialog."""
        try:
            from kivymd.uix.picker import MDDatePicker
            if self._selected_date:
                picker = MDDatePicker(
                    year=self._selected_date.year,
                    month=self._selected_date.month,
                    day=self._selected_date.day,
                )
            else:
                today = date.today()
                picker = MDDatePicker(
                    year=today.year,
                    month=today.month,
                    day=today.day,
                )
            picker.bind(on_save=self._on_date_selected, on_cancel=lambda i, v: i.dismiss())
            picker.open()
        except Exception as e:
            self._show_error_dialog("Date Picker Error", f"Could not open date picker: {str(e)}")

    def _on_date_selected(self, instance, selected_date, date_range):
        """Callback when a date is chosen in the date picker."""
        try:
            self._selected_date = selected_date
            self.ids.date_display_field.text = selected_date.isoformat()
            instance.dismiss()
            if self._selected_class_id:
                self._load_students_for_attendance()
        except Exception as e:
            self._show_error_dialog("Error", str(e))

    # ------------------------------------------------------------------
    # Load students and build attendance rows
    # ------------------------------------------------------------------

    def _load_students_for_attendance(self):
        """Load students for the selected class and build attendance rows."""
        try:
            if not self._selected_class_id:
                return

            self.ids.student_rows.clear_widgets()
            self._student_status = {}
            self._students = []

            app = App.get_running_app()
            students = app.db.get_students_by_class(self._selected_class_id)

            if not students:
                self.ids.attendance_title_lbl.text = "No students in this class"
                self.ids.student_rows.add_widget(
                    MDLabel(
                        text="No students enrolled in this class.",
                        halign="center",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(48),
                    )
                )
                return

            self._students = students
            date_str = (
                self._selected_date.isoformat()
                if self._selected_date
                else date.today().isoformat()
            )

            # Check if attendance already recorded for this date
            existing = app.db.get_attendance_by_class_date(
                self._selected_class_id, date_str
            )
            existing_map = {rec["student_id"]: rec["status"] for rec in existing}

            self.ids.attendance_title_lbl.text = (
                f"Students — {self._selected_class_name} ({len(students)} enrolled)"
            )

            for student in students:
                sid = student["id"]
                pre_status = existing_map.get(sid, None)
                row = self._build_attendance_row(student, pre_status)
                self.ids.student_rows.add_widget(row)
        except Exception as e:
            self._show_error_dialog("Load Error", f"Failed to load students: {str(e)}")

    def _build_attendance_row(self, student: dict, pre_status=None) -> MDBoxLayout:
        """Build a row widget with Present / Absent / Late toggle buttons."""
        try:
            sid = student["id"]
            # Default status to pre_status or None
            self._student_status[sid] = pre_status

            row = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(68),
                radius=[8, 8, 8, 8],
                elevation=0.5,
                padding=[dp(12), dp(6), dp(12), dp(6)],
                spacing=dp(8),
                md_bg_color=(0.97, 0.97, 0.97, 1),
            )

            # Student name label
            name_lbl = MDLabel(
                text=student.get("full_name", "Unknown"),
                font_style="Caption",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.15, 0.15, 0.15, 1),
                size_hint_x=0.35,
            )

            # Three toggle buttons
            btn_present = MDRaisedButton(
                text="P",
                size_hint=(None, None),
                size=(dp(44), dp(36)),
                md_bg_color=(
                    (76/255, 175/255, 80/255, 1)
                    if pre_status == "Present"
                    else (0.8, 0.8, 0.8, 1)
                ),
            )
            btn_absent = MDRaisedButton(
                text="A",
                size_hint=(None, None),
                size=(dp(44), dp(36)),
                md_bg_color=(
                    (244/255, 67/255, 54/255, 1)
                    if pre_status == "Absent"
                    else (0.8, 0.8, 0.8, 1)
                ),
            )
            btn_late = MDRaisedButton(
                text="L",
                size_hint=(None, None),
                size=(dp(44), dp(36)),
                md_bg_color=(
                    (255/255, 152/255, 0/255, 1)
                    if pre_status == "Late"
                    else (0.8, 0.8, 0.8, 1)
                ),
            )

            def make_handler(student_id, status, b_p, b_a, b_l):
                def handler(btn):
                    self._student_status[student_id] = status
                    b_p.md_bg_color = (
                        (76/255, 175/255, 80/255, 1)
                        if status == "Present" else (0.8, 0.8, 0.8, 1)
                    )
                    b_a.md_bg_color = (
                        (244/255, 67/255, 54/255, 1)
                        if status == "Absent" else (0.8, 0.8, 0.8, 1)
                    )
                    b_l.md_bg_color = (
                        (255/255, 152/255, 0/255, 1)
                        if status == "Late" else (0.8, 0.8, 0.8, 1)
                    )
                return handler

            btn_present.bind(on_release=make_handler(
                sid, "Present", btn_present, btn_absent, btn_late))
            btn_absent.bind(on_release=make_handler(
                sid, "Absent", btn_present, btn_absent, btn_late))
            btn_late.bind(on_release=make_handler(
                sid, "Late", btn_present, btn_absent, btn_late))

            row.add_widget(name_lbl)
            row.add_widget(btn_present)
            row.add_widget(btn_absent)
            row.add_widget(btn_late)
            return row
        except Exception as e:
            print(f"[AttendanceScreen] _build_attendance_row error: {e}")
            fb = MDCard(size_hint_y=None, height=dp(50))
            fb.add_widget(MDLabel(text="Row error", halign="center"))
            return fb

    # ------------------------------------------------------------------
    # Save attendance
    # ------------------------------------------------------------------

    def save_attendance(self):
        """Iterate through all students and save their attendance status."""
        try:
            if not self._selected_class_id:
                self._show_error_dialog("Error", "Please select a class first.")
                return
            if not self._students:
                self._show_error_dialog("Error", "No students to record attendance for.")
                return

            date_str = (
                self._selected_date.isoformat()
                if self._selected_date
                else date.today().isoformat()
            )

            app = App.get_running_app()
            unmarked = []
            saved = 0
            errors = 0

            for student in self._students:
                sid = student["id"]
                status = self._student_status.get(sid)
                if not status:
                    unmarked.append(student.get("full_name", str(sid)))
                    continue
                ok = app.db.mark_attendance(
                    sid, self._selected_class_id, date_str, status
                )
                if ok:
                    saved += 1
                else:
                    errors += 1

            if unmarked:
                self._show_error_dialog(
                    "Unmarked Students",
                    f"The following students have no status selected:\n"
                    + ", ".join(unmarked)
                    + "\n\nPlease mark P / A / L for every student."
                )
                return

            if errors > 0:
                self._show_error_dialog(
                    "Partial Save",
                    f"Saved {saved} records, but {errors} failed. Please try again."
                )
            else:
                Snackbar(
                    text=f"Attendance saved for {date_str} ({saved} students)."
                ).open()
        except Exception as e:
            self._show_error_dialog("Save Error", f"Failed to save attendance: {str(e)}")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def go_back(self):
        """Navigate back to the dashboard."""
        try:
            self.manager.current = "dashboard"
        except Exception as e:
            print(f"[AttendanceScreen] go_back error: {e}")

    def go_report(self):
        """Navigate to the attendance report screen."""
        try:
            self.manager.current = "attendance_report"
        except Exception as e:
            print(f"[AttendanceScreen] go_report error: {e}")

    def _show_error_dialog(self, title: str, message: str):
        """Show a modal error dialog."""
        try:
            if self._error_dialog:
                self._error_dialog.dismiss()
            self._error_dialog = MDDialog(
                title=title,
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self._error_dialog.dismiss()
                    )
                ]
            )
            self._error_dialog.open()
        except Exception as e:
            print(f"[AttendanceScreen] _show_error_dialog failed: {e}")
