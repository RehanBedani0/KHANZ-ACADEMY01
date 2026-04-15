# File: screens/add_class_screen.py
"""
Add / Edit Class Screen — Form to create or update a class record.
All KV layout is embedded inline via Builder.load_string().
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.snackbar import Snackbar

Builder.load_string("""
<AddClassScreen>:
    name: "add_class"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 245/255, 245/255, 245/255, 1

        MDTopAppBar:
            id: top_bar
            title: "Add Class"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 2

        ScrollView:

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "16dp"
                spacing: "16dp"

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    radius: [16, 16, 16, 16]
                    elevation: 1.5
                    padding: "20dp"
                    spacing: "16dp"
                    md_bg_color: 1, 1, 1, 1

                    MDLabel:
                        text: "Class Information"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 38/255, 166/255, 154/255, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(8)

                    MDTextField:
                        id: class_name_field
                        hint_text: "Class Name *"
                        icon_left: "google-classroom"
                        mode: "rectangle"
                        size_hint_y: None
                        height: "56dp"
                        helper_text_mode: "on_error"

                    MDTextField:
                        id: teacher_name_field
                        hint_text: "Teacher Name *"
                        icon_left: "account-tie"
                        mode: "rectangle"
                        size_hint_y: None
                        height: "56dp"
                        helper_text_mode: "on_error"

                    MDTextField:
                        id: monthly_fee_field
                        hint_text: "Monthly Fee (Rs.)"
                        icon_left: "cash"
                        input_filter: "float"
                        mode: "rectangle"
                        size_hint_y: None
                        height: "56dp"
                        helper_text_mode: "on_error"

                    MDTextField:
                        id: schedule_field
                        hint_text: "Schedule (e.g. Mon/Wed/Fri 4-6 PM)"
                        icon_left: "calendar-clock"
                        mode: "rectangle"
                        size_hint_y: None
                        height: "56dp"

                MDRaisedButton:
                    id: save_btn
                    text: "SAVE CLASS"
                    size_hint_x: 1
                    size_hint_y: None
                    height: "52dp"
                    md_bg_color: 38/255, 166/255, 154/255, 1
                    on_release: root.on_save()

                Widget:
                    size_hint_y: None
                    height: "16dp"
""")


class AddClassScreen(MDScreen):
    """Form screen for adding a new class or editing an existing one."""

    name = "add_class"
    _error_dialog = None

    def on_pre_enter(self):
        """
        Populate fields if editing an existing class (app.current_class_id is set),
        or clear all fields if adding a new one.
        """
        try:
            app = App.get_running_app()
            class_id = getattr(app, "current_class_id", None)
            if class_id:
                self.ids.top_bar.title = "Edit Class"
                self.ids.save_btn.text = "UPDATE CLASS"
                self.load_class(class_id)
            else:
                self.ids.top_bar.title = "Add Class"
                self.ids.save_btn.text = "SAVE CLASS"
                self.clear_form()
        except Exception as e:
            self._show_error_dialog("Error", f"Failed to initialize form: {str(e)}")

    def refresh_data(self):
        """Nothing extra needed — on_pre_enter handles data loading."""
        pass

    def load_class(self, class_id: int):
        """Load existing class data into the form fields."""
        try:
            app = App.get_running_app()
            cls = app.db.get_class_by_id(class_id)
            if not cls:
                self._show_error_dialog("Error", "Class record not found.")
                return

            self.ids.class_name_field.text = cls.get("class_name", "")
            self.ids.teacher_name_field.text = cls.get("teacher_name", "")
            self.ids.monthly_fee_field.text = str(cls.get("monthly_fee", "0"))
            self.ids.schedule_field.text = cls.get("schedule", "")
        except Exception as e:
            self._show_error_dialog("Load Error", f"Failed to load class data: {str(e)}")

    def clear_form(self):
        """Clear all form fields."""
        try:
            for fid in ("class_name_field", "teacher_name_field",
                        "monthly_fee_field", "schedule_field"):
                field = self.ids[fid]
                field.text = ""
                field.error = False
                field.helper_text = ""
        except Exception as e:
            print(f"[AddClassScreen] clear_form error: {e}")

    def on_save(self):
        """Validate the form and save or update the class record."""
        try:
            class_name = self.ids.class_name_field.text.strip()
            teacher_name = self.ids.teacher_name_field.text.strip()
            fee_text = self.ids.monthly_fee_field.text.strip()
            schedule = self.ids.schedule_field.text.strip()

            # Validation
            has_error = False

            if not class_name:
                self.ids.class_name_field.error = True
                self.ids.class_name_field.helper_text = "Class name is required"
                self.ids.class_name_field.helper_text_mode = "on_error"
                has_error = True
            else:
                self.ids.class_name_field.error = False
                self.ids.class_name_field.helper_text = ""

            if not teacher_name:
                self.ids.teacher_name_field.error = True
                self.ids.teacher_name_field.helper_text = "Teacher name is required"
                self.ids.teacher_name_field.helper_text_mode = "on_error"
                has_error = True
            else:
                self.ids.teacher_name_field.error = False
                self.ids.teacher_name_field.helper_text = ""

            if has_error:
                return

            # Parse monthly fee safely
            try:
                monthly_fee = float(fee_text) if fee_text else 0.0
            except ValueError:
                self.ids.monthly_fee_field.error = True
                self.ids.monthly_fee_field.helper_text = "Enter a valid number"
                self.ids.monthly_fee_field.helper_text_mode = "on_error"
                return

            app = App.get_running_app()
            class_id = getattr(app, "current_class_id", None)

            if class_id:
                # Edit mode
                success = app.db.update_class(
                    class_id, class_name, teacher_name, monthly_fee, schedule
                )
                if success:
                    Snackbar(text="Class updated successfully!").open()
                    app.current_class_id = None
                    self.manager.current = "class_list"
                else:
                    self._show_error_dialog(
                        "Error", "Failed to update class. Please try again."
                    )
            else:
                # Add mode
                new_id = app.db.add_class(
                    class_name, teacher_name, monthly_fee, schedule
                )
                if new_id:
                    Snackbar(text="Class added successfully!").open()
                    self.manager.current = "class_list"
                else:
                    self._show_error_dialog(
                        "Error", "Failed to add class. Please try again."
                    )
        except Exception as e:
            self._show_error_dialog("Unexpected Error", f"An error occurred: {str(e)}")

    def go_back(self):
        """Navigate back to the class list without saving."""
        try:
            app = App.get_running_app()
            app.current_class_id = None
            self.manager.current = "class_list"
        except Exception as e:
            print(f"[AddClassScreen] go_back error: {e}")

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
            print(f"[AddClassScreen] _show_error_dialog failed: {e}")
