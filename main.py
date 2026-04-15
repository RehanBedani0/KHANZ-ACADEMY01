# File: main.py

import os
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window

# Import ALL screens
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.student_list_screen import StudentListScreen
from screens.add_student_screen import AddStudentScreen
from screens.class_list_screen import ClassListScreen
from screens.add_class_screen import AddClassScreen
from screens.attendance_screen import AttendanceScreen
from screens.attendance_report_screen import AttendanceReportScreen
from screens.fee_management_screen import FeeManagementScreen
from screens.fee_voucher_screen import FeeVoucherScreen
from libs.database import DatabaseManager

# CRITICAL: Set keyboard mode BEFORE app starts
Window.softinput_mode = "below_target"


class KhanzAcademyApp(MDApp):
    """Main application class for Khan'z Academy Manager."""

    def build(self):
        # Theme configuration
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        # material_style M3 is supported in KivyMD 1.1.1
        try:
            self.theme_cls.material_style = "M3"
        except Exception:
            pass  # Fall back silently if version doesn't support it

        # Initialize database
        self.db = DatabaseManager()

        # Current context attributes used for inter-screen data passing
        self.current_student_id = None
        self.current_class_id = None
        self.current_fee_id = None

        # Screen Manager with slide transition
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(StudentListScreen(name="student_list"))
        sm.add_widget(AddStudentScreen(name="add_student"))
        sm.add_widget(ClassListScreen(name="class_list"))
        sm.add_widget(AddClassScreen(name="add_class"))
        sm.add_widget(AttendanceScreen(name="attendance"))
        sm.add_widget(AttendanceReportScreen(name="attendance_report"))
        sm.add_widget(FeeManagementScreen(name="fee_management"))
        sm.add_widget(FeeVoucherScreen(name="fee_voucher"))

        return sm

    def on_stop(self):
        """Called when the application is closing."""
        pass


if __name__ == "__main__":
    KhanzAcademyApp().run()
