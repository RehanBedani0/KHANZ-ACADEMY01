# File: screens/login_screen.py
"""
Login Screen — PIN-based authentication for Khan'z Academy Manager.
All KV layout is embedded inline via Builder.load_string().
"""

from kivy.lang import Builder
from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

Builder.load_string("""
<LoginScreen>:
    name: "login"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.theme_cls.bg_normal

        # Vertically center the card
        Widget:
            size_hint_y: 0.1

        ScrollView:
            size_hint_y: 0.8

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "32dp"
                spacing: "0dp"

                MDCard:
                    orientation: "vertical"
                    size_hint_x: 1
                    size_hint_y: None
                    height: self.minimum_height
                    radius: [20, 20, 20, 20]
                    elevation: 4
                    padding: "32dp"
                    spacing: "16dp"
                    md_bg_color: 1, 1, 1, 1

                    MDIcon:
                        id: logo_icon
                        icon: "school"
                        halign: "center"
                        font_size: "80sp"
                        theme_text_color: "Custom"
                        text_color: 63/255, 81/255, 181/255, 1
                        size_hint_y: None
                        height: "90sp"

                    MDLabel:
                        text: "Khan'z Academy"
                        font_style: "H4"
                        halign: "center"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 63/255, 81/255, 181/255, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(8)

                    MDLabel:
                        text: "Management System"
                        font_style: "Subtitle1"
                        halign: "center"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(8)

                    Widget:
                        size_hint_y: None
                        height: "8dp"

                    MDTextField:
                        id: pin_field
                        hint_text: "Enter PIN"
                        password: True
                        max_text_length: 4
                        input_filter: "int"
                        mode: "rectangle"
                        size_hint_y: None
                        height: "56dp"
                        on_text_validate: root.do_login()

                    Widget:
                        size_hint_y: None
                        height: "8dp"

                    MDRaisedButton:
                        id: login_btn
                        text: "LOGIN"
                        size_hint_x: 1
                        size_hint_y: None
                        height: "52dp"
                        md_bg_color: 63/255, 81/255, 181/255, 1
                        on_release: root.do_login()

                    Widget:
                        size_hint_y: None
                        height: "8dp"

                    MDLabel:
                        text: "Default PIN: 1234"
                        font_style: "Caption"
                        halign: "center"
                        theme_text_color: "Hint"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(4)

        Widget:
            size_hint_y: 0.1
""")


class LoginScreen(MDScreen):
    """PIN-based login screen. Navigates to dashboard on success."""

    name = "login"
    _error_dialog = None

    def on_pre_enter(self):
        """Called every time the screen is about to be shown. Clear the PIN field."""
        self.refresh_data()

    def refresh_data(self):
        """Clear PIN input field each time the screen is entered."""
        try:
            self.ids.pin_field.text = ""
            self.ids.pin_field.error = False
            self.ids.pin_field.helper_text = ""
        except Exception as e:
            print(f"[LoginScreen] refresh_data error: {e}")

    def do_login(self):
        """Validate PIN against the database and navigate to dashboard on success."""
        try:
            pin_text = self.ids.pin_field.text.strip()

            if not pin_text:
                self.ids.pin_field.error = True
                self.ids.pin_field.helper_text = "PIN cannot be empty"
                self.ids.pin_field.helper_text_mode = "on_error"
                return

            app = App.get_running_app()
            is_valid = app.db.verify_pin(pin_text)

            if is_valid:
                self.ids.pin_field.error = False
                self.manager.current = "dashboard"
            else:
                self.ids.pin_field.error = True
                self.ids.pin_field.helper_text = "Wrong PIN"
                self.ids.pin_field.helper_text_mode = "on_error"
                self._show_error_dialog(
                    "Invalid PIN",
                    "The PIN you entered is incorrect.\nDefault PIN is 1234."
                )
        except Exception as e:
            self._show_error_dialog(
                "Error",
                f"An unexpected error occurred: {str(e)}"
            )

    def _show_error_dialog(self, title: str, message: str):
        """Show a modal error dialog to the user."""
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
            print(f"[LoginScreen] _show_error_dialog error: {e}")
