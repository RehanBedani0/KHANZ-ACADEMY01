# File: screens/attendance_report_screen.py
"""
Attendance Report Screen — View per-student attendance summary for a class/month.
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
from kivymd.uix.list import TwoLineListItem, MDList

# Month names for the picker
MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December",
]

Builder.load_string("""
<AttendanceReportScreen>:
    name: "attendance_report"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 245/255, 245/255, 245/255, 1

        MDTopAppBar:
            title: "Attendance Report"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 2

        ScrollView:

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "12dp"
                spacing: "12dp"

                # ── Filter Card ──────────────────────────────────────────
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
                        text: "Filter Report"
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

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "52dp"
                        spacing: "8dp"

                        MDTextField:
                            id: month_display_field
                            hint_text: "Month"
                            icon_left: "calendar-month"
                            mode: "rectangle"
                            readonly: True
                            on_focus: if self.focus: root.show_month_picker()

                        MDTextField:
                            id: year_display_field
                            hint_text: "Year"
                            icon_left: "calendar"
                            input_filter: "int"
                            mode: "rectangle"
                            size_hint_x: 0.45

                    MDRaisedButton:
                        text: "GENERATE REPORT"
                        size_hint_x: 1
                        size_hint_y: None
                        height: "48dp"
                        md_bg_color: 63/255, 81/255, 181/255, 1
                        on_release: root.generate_report()

                # ── Report Header Row ────────────────────────────────────
                MDCard:
                    id: report_header_card
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "40dp"
                    radius: [8, 8, 0, 0]
                    elevation: 0.5
                    padding: "12dp", "4dp", "12dp", "4dp"
                    spacing: "4dp"
                    md_bg_color: 63/255, 81/255, 181/255, 1
                    opacity: 0

                    MDLabel:
                        text: "Student"
                        font_style: "Caption"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_x: 0.35

                    MDLabel:
                        text: "P"
                        halign: "center"
                        font_style: "Caption"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_x: 0.13

                    MDLabel:
                        text: "A"
                        halign: "center"
                        font_style: "Caption"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_x: 0.13

                    MDLabel:
                        text: "L"
                        halign: "center"
                        font_style: "Caption"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_x: 0.13

                    MDLabel:
                        text: "%"
                        halign: "center"
                        font_style: "Caption"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_x: 0.26

                # ── Report Rows Container ────────────────────────────────
                MDBoxLayout:
                    id: report_container
                    orientation: "vertical"
                    adaptive_height: True
                    spacing: "2dp"

                Widget:
                    size_hint_y: None
                    height: "16dp"
""")


class AttendanceReportScreen(MDScreen):
    """Displays monthly attendance summary per student for a selected class."""

    name = "attendance_report"
    _selected_class_id = None
    _selected_class_name = ""
    _selected_month = None
    _class_picker_dialog = None
    _month_picker_dialog = None
    _error_dialog = None

    def on_pre_enter(self):
        """Reset the report screen each time it is shown."""
        self.refresh_data()

    def refresh_data(self):
        """Clear previous report data and reset fields."""
        try:
            today = date.today()
            self._selected_class_id = None
            self._selected_class_name = ""
            self._selected_month = MONTHS[today.month - 1]

            self.ids.class_display_field.text = ""
            self.ids.month_display_field.text = self._selected_month
            self.ids.year_display_field.text = str(today.year)
            self.ids.report_container.clear_widgets()
            self.ids.report_header_card.opacity = 0
        except Exception as e:
            print(f"[AttendanceReportScreen] refresh_data error: {e}")

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
        """Handle class selection callback."""
        try:
            self._selected_class_id = class_id
            self._selected_class_name = class_name
            self.ids.class_display_field.text = class_name
            if self._class_picker_dialog:
                self._class_picker_dialog.dismiss()
        except Exception as e:
            print(f"[AttendanceReportScreen] _select_class error: {e}")

    # ------------------------------------------------------------------
    # Month picker
    # ------------------------------------------------------------------

    def show_month_picker(self):
        """Show a dialog to select a month by name."""
        try:
            if self._month_picker_dialog:
                self._month_picker_dialog.dismiss()

            list_widget = MDList()
            from kivy.uix.scrollview import ScrollView as KVScrollView
            scroll = KVScrollView(size_hint_y=None, height=dp(300))

            for month_name in MONTHS:
                item = TwoLineListItem(
                    text=month_name,
                    secondary_text="",
                )
                m = month_name
                item.bind(on_release=lambda x, mn=m: self._select_month(mn))
                list_widget.add_widget(item)

            scroll.add_widget(list_widget)

            self._month_picker_dialog = MDDialog(
                title="Select Month",
                type="custom",
                content_cls=scroll,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self._month_picker_dialog.dismiss()
                    )
                ]
            )
            self._month_picker_dialog.open()
        except Exception as e:
            self._show_error_dialog("Error", f"Could not open month picker: {str(e)}")

    def _select_month(self, month_name: str):
        """Handle month selection callback."""
        try:
            self._selected_month = month_name
            self.ids.month_display_field.text = month_name
            if self._month_picker_dialog:
                self._month_picker_dialog.dismiss()
        except Exception as e:
            print(f"[AttendanceReportScreen] _select_month error: {e}")

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_report(self):
        """Fetch and display the attendance report for the selected filters."""
        try:
            if not self._selected_class_id:
                self._show_error_dialog("Error", "Please select a class.")
                return

            month_str = self.ids.month_display_field.text.strip()
            year_str = self.ids.year_display_field.text.strip()

            if not month_str:
                self._show_error_dialog("Error", "Please select a month.")
                return
            if not year_str:
                self._show_error_dialog("Error", "Please enter a year.")
                return

            try:
                year = int(year_str)
            except ValueError:
                self._show_error_dialog("Error", "Year must be a valid number.")
                return

            # Month number (1-based) from name
            try:
                month_num = MONTHS.index(month_str) + 1
            except ValueError:
                month_num = 1

            month_padded = str(month_num).zfill(2)

            app = App.get_running_app()
            records = app.db.get_attendance_report(
                self._selected_class_id, month_padded, year
            )

            self.ids.report_container.clear_widgets()

            if not records:
                self.ids.report_header_card.opacity = 0
                self.ids.report_container.add_widget(
                    MDLabel(
                        text="No attendance records found for the selected period.",
                        halign="center",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(60),
                    )
                )
                return

            self.ids.report_header_card.opacity = 1
            for i, rec in enumerate(records):
                row = self._build_report_row(rec, alternate=(i % 2 == 0))
                self.ids.report_container.add_widget(row)
        except Exception as e:
            self._show_error_dialog("Report Error", f"Failed to generate report: {str(e)}")

    def _build_report_row(self, rec: dict, alternate: bool = False) -> MDBoxLayout:
        """Build a single report data row."""
        try:
            pct = rec.get("pct", 0.0)
            # Color the percentage
            if pct >= 75:
                pct_color = (76/255, 175/255, 80/255, 1)
            elif pct >= 50:
                pct_color = (255/255, 152/255, 0/255, 1)
            else:
                pct_color = (244/255, 67/255, 54/255, 1)

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(42),
                padding=[dp(12), dp(4), dp(12), dp(4)],
                spacing=dp(4),
                md_bg_color=(
                    (0.95, 0.95, 0.95, 1) if alternate else (1, 1, 1, 1)
                ),
            )

            name_lbl = MDLabel(
                text=rec.get("full_name", "Unknown"),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.15, 0.15, 0.15, 1),
                size_hint_x=0.35,
            )
            present_lbl = MDLabel(
                text=str(rec.get("present", 0) or 0),
                halign="center",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(76/255, 175/255, 80/255, 1),
                size_hint_x=0.13,
            )
            absent_lbl = MDLabel(
                text=str(rec.get("absent", 0) or 0),
                halign="center",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(244/255, 67/255, 54/255, 1),
                size_hint_x=0.13,
            )
            late_lbl = MDLabel(
                text=str(rec.get("late", 0) or 0),
                halign="center",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(255/255, 152/255, 0/255, 1),
                size_hint_x=0.13,
            )
            pct_lbl = MDLabel(
                text=f"{pct:.1f}%",
                halign="center",
                font_style="Caption",
                bold=True,
                theme_text_color="Custom",
                text_color=pct_color,
                size_hint_x=0.26,
            )

            row.add_widget(name_lbl)
            row.add_widget(present_lbl)
            row.add_widget(absent_lbl)
            row.add_widget(late_lbl)
            row.add_widget(pct_lbl)
            return row
        except Exception as e:
            print(f"[AttendanceReportScreen] _build_report_row error: {e}")
            fb = MDBoxLayout(size_hint_y=None, height=dp(40))
            fb.add_widget(MDLabel(text="Row error", halign="center"))
            return fb

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def go_back(self):
        """Navigate back to the attendance mark screen."""
        try:
            self.manager.current = "attendance"
        except Exception as e:
            print(f"[AttendanceReportScreen] go_back error: {e}")

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
            print(f"[AttendanceReportScreen] _show_error_dialog failed: {e}")
