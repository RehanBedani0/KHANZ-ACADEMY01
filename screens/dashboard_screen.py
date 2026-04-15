# File: screens/dashboard_screen.py
"""
Dashboard Screen — Shows summary statistics and the navigation drawer.
All KV layout is embedded inline via Builder.load_string().
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationLayout,
    MDNavigationDrawerMenu,
    MDNavigationDrawerItem,
)

Builder.load_string("""
<DashboardScreen>:
    name: "dashboard"

    MDNavigationLayout:

        MDScreenManager:
            MDScreen:

                MDBoxLayout:
                    orientation: "vertical"
                    md_bg_color: 245/255, 245/255, 245/255, 1

                    MDTopAppBar:
                        title: "Dashboard"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                        right_action_items: [["logout", lambda x: root.do_logout()]]
                        elevation: 2

                    ScrollView:

                        MDBoxLayout:
                            id: main_content
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            padding: "16dp"
                            spacing: "16dp"

                            MDLabel:
                                text: "Overview"
                                font_style: "H6"
                                bold: True
                                size_hint_y: None
                                height: self.texture_size[1] + dp(8)

                            # ── 2-column stats grid ──────────────────────────
                            MDGridLayout:
                                id: stats_grid
                                cols: 2
                                adaptive_height: True
                                spacing: "12dp"

                                # Stat Card 1 — Total Students
                                MDCard:
                                    id: card_students
                                    orientation: "vertical"
                                    size_hint_y: None
                                    height: "140dp"
                                    radius: [15, 15, 15, 15]
                                    elevation: 1.5
                                    padding: "16dp"
                                    spacing: "4dp"
                                    md_bg_color: 1, 1, 1, 1

                                    MDIcon:
                                        icon: "account-group"
                                        halign: "center"
                                        font_size: "36sp"
                                        theme_text_color: "Custom"
                                        text_color: 63/255, 81/255, 181/255, 1

                                    MDLabel:
                                        id: lbl_total_students
                                        text: "0"
                                        halign: "center"
                                        font_style: "H5"
                                        bold: True
                                        theme_text_color: "Custom"
                                        text_color: 0.1, 0.1, 0.1, 1

                                    MDLabel:
                                        text: "Total Students"
                                        halign: "center"
                                        font_style: "Caption"
                                        theme_text_color: "Secondary"

                                # Stat Card 2 — Total Classes
                                MDCard:
                                    id: card_classes
                                    orientation: "vertical"
                                    size_hint_y: None
                                    height: "140dp"
                                    radius: [15, 15, 15, 15]
                                    elevation: 1.5
                                    padding: "16dp"
                                    spacing: "4dp"
                                    md_bg_color: 1, 1, 1, 1

                                    MDIcon:
                                        icon: "google-classroom"
                                        halign: "center"
                                        font_size: "36sp"
                                        theme_text_color: "Custom"
                                        text_color: 38/255, 166/255, 154/255, 1

                                    MDLabel:
                                        id: lbl_total_classes
                                        text: "0"
                                        halign: "center"
                                        font_style: "H5"
                                        bold: True
                                        theme_text_color: "Custom"
                                        text_color: 0.1, 0.1, 0.1, 1

                                    MDLabel:
                                        text: "Total Classes"
                                        halign: "center"
                                        font_style: "Caption"
                                        theme_text_color: "Secondary"

                                # Stat Card 3 — Revenue This Month
                                MDCard:
                                    id: card_revenue
                                    orientation: "vertical"
                                    size_hint_y: None
                                    height: "140dp"
                                    radius: [15, 15, 15, 15]
                                    elevation: 1.5
                                    padding: "16dp"
                                    spacing: "4dp"
                                    md_bg_color: 1, 1, 1, 1

                                    MDIcon:
                                        icon: "cash"
                                        halign: "center"
                                        font_size: "36sp"
                                        theme_text_color: "Custom"
                                        text_color: 76/255, 175/255, 80/255, 1

                                    MDLabel:
                                        id: lbl_revenue
                                        text: "Rs. 0"
                                        halign: "center"
                                        font_style: "H6"
                                        bold: True
                                        theme_text_color: "Custom"
                                        text_color: 0.1, 0.1, 0.1, 1

                                    MDLabel:
                                        text: "Revenue (Month)"
                                        halign: "center"
                                        font_style: "Caption"
                                        theme_text_color: "Secondary"

                                # Stat Card 4 — Pending Fees
                                MDCard:
                                    id: card_pending
                                    orientation: "vertical"
                                    size_hint_y: None
                                    height: "140dp"
                                    radius: [15, 15, 15, 15]
                                    elevation: 1.5
                                    padding: "16dp"
                                    spacing: "4dp"
                                    md_bg_color: 1, 1, 1, 1

                                    MDIcon:
                                        icon: "alert-circle"
                                        halign: "center"
                                        font_size: "36sp"
                                        theme_text_color: "Custom"
                                        text_color: 255/255, 152/255, 0/255, 1

                                    MDLabel:
                                        id: lbl_pending
                                        text: "Rs. 0"
                                        halign: "center"
                                        font_style: "H6"
                                        bold: True
                                        theme_text_color: "Custom"
                                        text_color: 0.1, 0.1, 0.1, 1

                                    MDLabel:
                                        text: "Pending Fees"
                                        halign: "center"
                                        font_style: "Caption"
                                        theme_text_color: "Secondary"

                            # ── Today's Attendance Card ──────────────────────
                            MDCard:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "120dp"
                                radius: [15, 15, 15, 15]
                                elevation: 1.5
                                padding: "16dp"
                                spacing: "8dp"
                                md_bg_color: 1, 1, 1, 1

                                MDBoxLayout:
                                    orientation: "horizontal"
                                    adaptive_height: True
                                    spacing: "8dp"

                                    MDIcon:
                                        icon: "calendar-check"
                                        font_size: "28sp"
                                        theme_text_color: "Custom"
                                        text_color: 63/255, 81/255, 181/255, 1
                                        size_hint_x: None
                                        width: "36dp"

                                    MDLabel:
                                        text: "Today's Attendance"
                                        font_style: "Subtitle1"
                                        bold: True
                                        theme_text_color: "Custom"
                                        text_color: 0.2, 0.2, 0.2, 1

                                MDLabel:
                                    id: lbl_attendance
                                    text: "0% attendance recorded today"
                                    font_style: "Body1"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: self.texture_size[1] + dp(4)

                            # ── Quick Action Buttons ─────────────────────────
                            MDLabel:
                                text: "Quick Actions"
                                font_style: "H6"
                                bold: True
                                size_hint_y: None
                                height: self.texture_size[1] + dp(8)

                            MDGridLayout:
                                cols: 2
                                adaptive_height: True
                                spacing: "12dp"

                                MDRaisedButton:
                                    text: "STUDENTS"
                                    icon: "account-group"
                                    size_hint_x: 1
                                    size_hint_y: None
                                    height: "48dp"
                                    md_bg_color: 63/255, 81/255, 181/255, 1
                                    on_release: root.go_to("student_list")

                                MDRaisedButton:
                                    text: "CLASSES"
                                    icon: "google-classroom"
                                    size_hint_x: 1
                                    size_hint_y: None
                                    height: "48dp"
                                    md_bg_color: 38/255, 166/255, 154/255, 1
                                    on_release: root.go_to("class_list")

                                MDRaisedButton:
                                    text: "ATTENDANCE"
                                    icon: "calendar-check"
                                    size_hint_x: 1
                                    size_hint_y: None
                                    height: "48dp"
                                    md_bg_color: 63/255, 81/255, 181/255, 1
                                    on_release: root.go_to("attendance")

                                MDRaisedButton:
                                    text: "FEES"
                                    icon: "cash-multiple"
                                    size_hint_x: 1
                                    size_hint_y: None
                                    height: "48dp"
                                    md_bg_color: 76/255, 175/255, 80/255, 1
                                    on_release: root.go_to("fee_management")

                            Widget:
                                size_hint_y: None
                                height: "16dp"

        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)

            MDNavigationDrawerMenu:

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "80dp"
                    padding: "16dp", "12dp", "16dp", "8dp"
                    md_bg_color: 63/255, 81/255, 181/255, 1

                    MDLabel:
                        text: "Khan'z Academy"
                        font_style: "H6"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_y: None
                        height: "32dp"

                    MDLabel:
                        text: "Management System"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.85, 0.85, 1, 1
                        size_hint_y: None
                        height: "20dp"

                MDNavigationDrawerItem:
                    icon: "view-dashboard"
                    text: "Dashboard"
                    on_release:
                        nav_drawer.set_state("close")
                        root.go_to("dashboard")

                MDNavigationDrawerItem:
                    icon: "account-group"
                    text: "Students"
                    on_release:
                        nav_drawer.set_state("close")
                        root.go_to("student_list")

                MDNavigationDrawerItem:
                    icon: "google-classroom"
                    text: "Classes"
                    on_release:
                        nav_drawer.set_state("close")
                        root.go_to("class_list")

                MDNavigationDrawerItem:
                    icon: "calendar-check"
                    text: "Attendance"
                    on_release:
                        nav_drawer.set_state("close")
                        root.go_to("attendance")

                MDNavigationDrawerItem:
                    icon: "chart-bar"
                    text: "Attendance Report"
                    on_release:
                        nav_drawer.set_state("close")
                        root.go_to("attendance_report")

                MDNavigationDrawerItem:
                    icon: "cash-multiple"
                    text: "Fee Management"
                    on_release:
                        nav_drawer.set_state("close")
                        root.go_to("fee_management")

                MDNavigationDrawerItem:
                    icon: "lock-reset"
                    text: "Change PIN"
                    on_release:
                        nav_drawer.set_state("close")
                        root.show_change_pin_dialog()

                MDNavigationDrawerItem:
                    icon: "logout"
                    text: "Logout"
                    on_release:
                        nav_drawer.set_state("close")
                        root.do_logout()
""")


class DashboardScreen(MDScreen):
    """Main dashboard showing stats, quick actions, and navigation drawer."""

    name = "dashboard"
    _change_pin_dialog = None
    _info_dialog = None

    def on_pre_enter(self):
        """Refresh dashboard data each time the screen is shown."""
        self.refresh_data()

    def refresh_data(self):
        """Fetch latest stats from the database and update all labels."""
        try:
            app = App.get_running_app()
            stats = app.db.get_dashboard_stats()

            self.ids.lbl_total_students.text = str(stats.get("total_students", 0))
            self.ids.lbl_total_classes.text = str(stats.get("total_classes", 0))

            revenue = stats.get("revenue_this_month", 0.0)
            pending = stats.get("pending_fees", 0.0)
            self.ids.lbl_revenue.text = f"Rs. {revenue:,.0f}"
            self.ids.lbl_pending.text = f"Rs. {pending:,.0f}"

            att_pct = stats.get("attendance_today_pct", 0.0)
            self.ids.lbl_attendance.text = (
                f"{att_pct:.1f}% attendance recorded today"
            )
        except Exception as e:
            self._show_error_dialog("Dashboard Error", f"Failed to load stats: {str(e)}")

    def go_to(self, screen_name: str):
        """Navigate to the specified screen."""
        try:
            self.manager.current = screen_name
        except Exception as e:
            self._show_error_dialog("Navigation Error", str(e))

    def do_logout(self):
        """Log out and return to the login screen."""
        try:
            self.manager.current = "login"
        except Exception as e:
            self._show_error_dialog("Logout Error", str(e))

    def show_change_pin_dialog(self):
        """Show a dialog with old PIN / new PIN fields to change the admin PIN."""
        try:
            if self._change_pin_dialog:
                self._change_pin_dialog.dismiss()

            old_pin_field = MDTextField(
                hint_text="Current PIN",
                password=True,
                max_text_length=4,
                input_filter="int",
                mode="rectangle",
                size_hint_y=None,
                height=dp(56),
            )
            new_pin_field = MDTextField(
                hint_text="New PIN (4 digits)",
                password=True,
                max_text_length=4,
                input_filter="int",
                mode="rectangle",
                size_hint_y=None,
                height=dp(56),
            )
            confirm_pin_field = MDTextField(
                hint_text="Confirm New PIN",
                password=True,
                max_text_length=4,
                input_filter="int",
                mode="rectangle",
                size_hint_y=None,
                height=dp(56),
            )

            content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                padding=[dp(8), dp(8), dp(8), dp(8)],
                size_hint_y=None,
                height=dp(220),
            )
            content.add_widget(old_pin_field)
            content.add_widget(new_pin_field)
            content.add_widget(confirm_pin_field)

            def _do_change(btn):
                old_p = old_pin_field.text.strip()
                new_p = new_pin_field.text.strip()
                conf_p = confirm_pin_field.text.strip()

                if not old_p or not new_p or not conf_p:
                    self._show_error_dialog("Error", "All fields are required.")
                    return
                if len(new_p) < 4:
                    self._show_error_dialog("Error", "New PIN must be exactly 4 digits.")
                    return
                if new_p != conf_p:
                    self._show_error_dialog("Error", "New PIN and confirmation do not match.")
                    return

                app = App.get_running_app()
                success = app.db.update_pin(old_p, new_p)
                if success:
                    self._change_pin_dialog.dismiss()
                    Snackbar(text="PIN changed successfully!").open()
                else:
                    self._show_error_dialog(
                        "Error",
                        "Failed to change PIN. Check that your current PIN is correct."
                    )

            self._change_pin_dialog = MDDialog(
                title="Change PIN",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self._change_pin_dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="SAVE",
                        md_bg_color=(63/255, 81/255, 181/255, 1),
                        on_release=_do_change
                    ),
                ]
            )
            self._change_pin_dialog.open()
        except Exception as e:
            self._show_error_dialog("Error", f"Could not open Change PIN dialog: {str(e)}")

    def _show_error_dialog(self, title: str, message: str):
        """Show a modal error dialog."""
        try:
            if self._info_dialog:
                self._info_dialog.dismiss()
            self._info_dialog = MDDialog(
                title=title,
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self._info_dialog.dismiss()
                    )
                ]
            )
            self._info_dialog.open()
        except Exception as e:
            print(f"[DashboardScreen] _show_error_dialog failed: {e}")
