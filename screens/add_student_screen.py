# File: screens/add_student_screen.py
"""
Add / Edit Student Screen — Form to create or update a student record.
All KV layout is embedded inline via Builder.load_string().
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import TwoLineListItem, MDList
from kivymd.uix.snackbar import Snackbar

Builder.load_string("""
<AddStudentScreen>:
    name: "add_student"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 245/255, 245/255, 245/255, 1

        MDTopAppBar:
            id: top_bar
            title: "Add Student"
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
                        text: "Student Information"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 63/255, 81/255, 181/255, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(8)

                    MDTextField:
                        id: name_field
                        hint_text: "Full Name *"
                        icon_left: "account"
                        mode: "rectangle"
                        size_hint_y: None
                        height: "56dp"
                        helper_text_mode: "on_error"

                    MDTextField:
                        id: phone_field
                        hint_text: "Phone Number"
                        icon_left: "phone"
                        input_filter: "int"
                        mode: "rectangle"
                        size_hint_y: None
                        height: "56dp"

                    MDTextField:
                        id: class_display_field
                        hint_text: "Select Class (tap to choose)"
                        icon_left: "google-classroom"
                        mode: "rectangle"
                        readonly: True
                        size_hint_y: None
                        height: "56dp"
                        on_focus: if self.focus: root.show_class_picker()

                    MDRaisedButton:
                        text: "CHOOSE CLASS"
                        size_hint_x: 1
                        size_hint_y: None
                        height: "48dp"
                        md_bg_color: 38/255, 166/255, 154/255, 1
                        on_release: root.show_class_picker()

                MDRaisedButton:
                    id: save_btn
                    text: "SAVE STUDENT"
                    size_hint_x: 1
                    size_hint_y: None
                    height: "52dp"
                    md_bg_color: 63/255, 81/255, 181/255, 1
                    on_release: root.on_save()

                Widget:
                    size_hint_y: None
                    height: "16dp"
""")


class AddStudentScreen(MDScreen):
    """Form screen for adding a new student or editing an existing one."""

    name = "add_student"
    _selected_class_id = None
    _selected_class_name = ""
    _class_picker_dialog = None
    _error_dialog = None

    def on_pre_enter(self):
        """
        Populate fields if editing an existing student (app.current_student_id is set),
        or clear all fields if adding a new one.
        """
        try:
            app = App.get_running_app()
            student_id = getattr(app, "current_student_id", None)
            if student_id:
                self.ids.top_bar.title = "Edit Student"
                self.ids.save_btn.text = "UPDATE STUDENT"
                self.load_student(student_id)
            else:
                self.ids.top_bar.title = "Add Student"
                self.ids.save_btn.text = "SAVE STUDENT"
                self.clear_form()
        except Exception as e:
            self._show_error_dialog("Error", f"Failed to initialize form: {str(e)}")

    def refresh_data(self):
        """Called by on_pre_enter indirectly. Nothing extra needed here."""
        pass

    def load_student(self, student_id: int):
        """Load existing student data into the form fields."""
        try:
            app = App.get_running_app()
            student = app.db.get_student_by_id(student_id)
            if not student:
                self._show_error_dialog("Error", "Student record not found.")
                return

            self.ids.name_field.text = student.get("full_name", "")
            self.ids.phone_field.text = student.get("phone", "")

            class_id = student.get("class_id")
            class_name = student.get("class_name", "")
            if class_id:
                self._selected_class_id = class_id
                self._selected_class_name = class_name
                self.ids.class_display_field.text = class_name
            else:
                self._selected_class_id = None
                self._selected_class_name = ""
                self.ids.class_display_field.text = ""
        except Exception as e:
            self._show_error_dialog("Load Error", f"Failed to load student data: {str(e)}")

    def clear_form(self):
        """Clear all form fields and reset selections."""
        try:
            self.ids.name_field.text = ""
            self.ids.name_field.error = False
            self.ids.name_field.helper_text = ""
            self.ids.phone_field.text = ""
            self.ids.class_display_field.text = ""
            self._selected_class_id = None
            self._selected_class_name = ""
        except Exception as e:
            print(f"[AddStudentScreen] clear_form error: {e}")

    def show_class_picker(self):
        """Show a dialog with a scrollable list of all available classes."""
        try:
            if self._class_picker_dialog:
                self._class_picker_dialog.dismiss()

            app = App.get_running_app()
            classes = app.db.get_all_classes()

            if not classes:
                self._show_error_dialog(
                    "No Classes",
                    "No classes found. Please add a class first."
                )
                return

            list_widget = MDList()
            scroll = __import__("kivy.uix.scrollview", fromlist=["ScrollView"]).ScrollView(
                size_hint_y=None,
                height=min(dp(300), len(classes) * dp(64))
            )

            for cls in classes:
                item = TwoLineListItem(
                    text=cls["class_name"],
                    secondary_text=f"Teacher: {cls['teacher_name']}  |  "
                                   f"Fee: Rs. {cls['monthly_fee']:,.0f}",
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
        """Callback when a class is selected from the picker dialog."""
        try:
            self._selected_class_id = class_id
            self._selected_class_name = class_name
            self.ids.class_display_field.text = class_name
            if self._class_picker_dialog:
                self._class_picker_dialog.dismiss()
        except Exception as e:
            print(f"[AddStudentScreen] _select_class error: {e}")

    def on_save(self):
        """Validate the form and save or update the student record."""
        try:
            name = self.ids.name_field.text.strip()
            if not name:
                self.ids.name_field.error = True
                self.ids.name_field.helper_text = "Name is required"
                self.ids.name_field.helper_text_mode = "on_error"
                return

            # Clear validation error if name is present
            self.ids.name_field.error = False
            self.ids.name_field.helper_text = ""

            phone = self.ids.phone_field.text.strip()
            class_id = self._selected_class_id

            app = App.get_running_app()
            student_id = getattr(app, "current_student_id", None)

            if student_id:
                # Edit mode
                success = app.db.update_student(student_id, name, phone, class_id)
                if success:
                    Snackbar(text="Student updated successfully!").open()
                    app.current_student_id = None
                    self.manager.current = "student_list"
                else:
                    self._show_error_dialog(
                        "Error", "Failed to update student. Please try again."
                    )
            else:
                # Add mode
                new_id = app.db.add_student(name, phone, class_id)
                if new_id:
                    Snackbar(text="Student added successfully!").open()
                    self.manager.current = "student_list"
                else:
                    self._show_error_dialog(
                        "Error", "Failed to add student. Please try again."
                    )
        except Exception as e:
            self._show_error_dialog("Unexpected Error", f"An error occurred: {str(e)}")

    def go_back(self):
        """Navigate back to the student list without saving."""
        try:
            app = App.get_running_app()
            app.current_student_id = None
            self.manager.current = "student_list"
        except Exception as e:
            print(f"[AddStudentScreen] go_back error: {e}")

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
            print(f"[AddStudentScreen] _show_error_dialog failed: {e}")
