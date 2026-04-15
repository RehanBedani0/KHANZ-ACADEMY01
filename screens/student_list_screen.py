# File: screens/student_list_screen.py
"""
Student List Screen — Displays all students with search, edit, and delete.
All KV layout is embedded inline via Builder.load_string().
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDIcon

Builder.load_string("""
<StudentListScreen>:
    name: "student_list"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 245/255, 245/255, 245/255, 1

        MDTopAppBar:
            title: "Students"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["account-plus", lambda x: root.go_add_student()]]
            elevation: 2

        MDBoxLayout:
            orientation: "vertical"
            padding: "12dp", "8dp", "12dp", "0dp"
            size_hint_y: None
            height: "72dp"

            MDTextField:
                id: search_field
                hint_text: "Search by name or phone..."
                icon_left: "magnify"
                mode: "rectangle"
                size_hint_y: None
                height: "52dp"
                on_text: root.on_search_text(self.text)

        ScrollView:

            MDBoxLayout:
                id: container
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "12dp"
                spacing: "8dp"

    MDFloatingActionButton:
        icon: "plus"
        md_bg_color: 63/255, 81/255, 181/255, 1
        pos_hint: {"right": 0.97, "y": 0.03}
        on_release: root.go_add_student()
""")


class StudentListScreen(MDScreen):
    """Lists all students, supports search, edit, and delete operations."""

    name = "student_list"
    _delete_dialog = None
    _error_dialog = None
    _search_event = None

    def on_pre_enter(self):
        """Refresh student list each time the screen is shown."""
        try:
            if hasattr(self.ids, 'search_field'):
                self.ids.search_field.text = ""
        except Exception:
            pass
        self.refresh_data()

    def refresh_data(self, query: str = ""):
        """Clear the container and rebuild the student list from the database."""
        try:
            self.ids.container.clear_widgets()
            app = App.get_running_app()

            if query.strip():
                students = app.db.search_students(query)
            else:
                students = app.db.get_all_students()

            if not students:
                self._show_empty_state()
                return

            for student in students:
                card = self._build_student_card(student)
                self.ids.container.add_widget(card)
        except Exception as e:
            self._show_error_dialog("Load Error", f"Failed to load students: {str(e)}")

    def _show_empty_state(self):
        """Display an empty-state message when no students are found."""
        try:
            empty_box = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(200),
                spacing=dp(16),
                padding=[dp(16), dp(40), dp(16), dp(16)],
            )
            icon_lbl = MDIcon(
                icon="account-off",
                halign="center",
                font_size="64sp",
                theme_text_color="Custom",
                text_color=(0.6, 0.6, 0.6, 1),
            )
            text_lbl = MDLabel(
                text="No students found.\nTap + to add one.",
                halign="center",
                font_style="Subtitle1",
                theme_text_color="Secondary",
            )
            empty_box.add_widget(icon_lbl)
            empty_box.add_widget(text_lbl)
            self.ids.container.add_widget(empty_box)
        except Exception as e:
            print(f"[StudentListScreen] _show_empty_state error: {e}")

    def _build_student_card(self, student: dict) -> MDCard:
        """Build and return a student card widget for the given student dict."""
        try:
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(80),
                radius=[12, 12, 12, 12],
                elevation=1,
                padding=[dp(12), dp(8), dp(12), dp(8)],
                spacing=dp(12),
                md_bg_color=(1, 1, 1, 1),
                ripple_behavior=True,
            )

            # Left avatar icon
            avatar = MDIcon(
                icon="account-circle",
                font_size="40sp",
                theme_text_color="Custom",
                text_color=(63/255, 81/255, 181/255, 1),
                size_hint=(None, None),
                size=(dp(44), dp(44)),
            )

            # Center info
            info_box = MDBoxLayout(
                orientation="vertical",
                spacing=dp(2),
            )
            name_lbl = MDLabel(
                text=student.get("full_name", "Unknown"),
                font_style="Subtitle1",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1),
                size_hint_y=None,
                height=dp(28),
            )
            detail_lbl = MDLabel(
                text=f"Class: {student.get('class_name', 'N/A')}  |  "
                     f"Phone: {student.get('phone', 'N/A')}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(22),
            )
            info_box.add_widget(name_lbl)
            info_box.add_widget(detail_lbl)

            # Delete button
            sid = student.get("id")
            sname = student.get("full_name", "this student")

            delete_btn = MDIconButton(
                icon="delete",
                theme_text_color="Custom",
                text_color=(0.9, 0.1, 0.1, 0.8),
                size_hint=(None, None),
                size=(dp(40), dp(40)),
            )
            delete_btn.bind(on_release=lambda btn, s_id=sid, s_name=sname:
                            self._confirm_delete(s_id, s_name))

            # Edit on card press
            card.bind(on_release=lambda c, s_id=sid:
                      self._go_edit_student(s_id))

            card.add_widget(avatar)
            card.add_widget(info_box)
            card.add_widget(delete_btn)
            return card
        except Exception as e:
            print(f"[StudentListScreen] _build_student_card error: {e}")
            # Return minimal fallback card
            fb = MDCard(size_hint_y=None, height=dp(60))
            fb.add_widget(MDLabel(text="Error loading student", halign="center"))
            return fb

    def on_search_text(self, text: str):
        """Debounce search — wait 300ms after last keystroke before querying."""
        try:
            if self._search_event:
                self._search_event.cancel()
            self._search_event = Clock.schedule_once(
                lambda dt: self.refresh_data(text), 0.3
            )
        except Exception as e:
            print(f"[StudentListScreen] on_search_text error: {e}")

    def _confirm_delete(self, student_id: int, student_name: str):
        """Show a confirmation dialog before deleting a student."""
        try:
            if self._delete_dialog:
                self._delete_dialog.dismiss()
            self._delete_dialog = MDDialog(
                title="Delete Student",
                text=f"Are you sure you want to delete\n[b]{student_name}[/b]?\n"
                     "This action cannot be undone.",
                markup=True,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self._delete_dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="DELETE",
                        md_bg_color=(244/255, 67/255, 54/255, 1),
                        on_release=lambda x, sid=student_id:
                            self._do_delete(sid)
                    ),
                ]
            )
            self._delete_dialog.open()
        except Exception as e:
            self._show_error_dialog("Error", f"Could not open dialog: {str(e)}")

    def _do_delete(self, student_id: int):
        """Perform the deletion and refresh the list."""
        try:
            if self._delete_dialog:
                self._delete_dialog.dismiss()
            app = App.get_running_app()
            success = app.db.delete_student(student_id)
            if success:
                Snackbar(text="Student deleted successfully.").open()
                self.refresh_data()
            else:
                self._show_error_dialog("Error", "Failed to delete student. Please try again.")
        except Exception as e:
            self._show_error_dialog("Delete Error", f"Unexpected error: {str(e)}")

    def _go_edit_student(self, student_id: int):
        """Navigate to the Add/Edit student screen in edit mode."""
        try:
            app = App.get_running_app()
            app.current_student_id = student_id
            self.manager.current = "add_student"
        except Exception as e:
            self._show_error_dialog("Navigation Error", str(e))

    def go_add_student(self):
        """Navigate to the Add/Edit student screen in add mode."""
        try:
            app = App.get_running_app()
            app.current_student_id = None
            self.manager.current = "add_student"
        except Exception as e:
            self._show_error_dialog("Navigation Error", str(e))

    def go_back(self):
        """Navigate back to the dashboard."""
        try:
            self.manager.current = "dashboard"
        except Exception as e:
            print(f"[StudentListScreen] go_back error: {e}")

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
            print(f"[StudentListScreen] _show_error_dialog failed: {e}")
