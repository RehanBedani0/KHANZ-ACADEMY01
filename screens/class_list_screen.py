# File: screens/class_list_screen.py
"""
Class List Screen — Displays all classes with edit and delete options.
All KV layout is embedded inline via Builder.load_string().
"""

from kivy.lang import Builder
from kivy.app import App
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
<ClassListScreen>:
    name: "class_list"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 245/255, 245/255, 245/255, 1

        MDTopAppBar:
            title: "Classes"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["plus", lambda x: root.go_add_class()]]
            elevation: 2

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
        md_bg_color: 38/255, 166/255, 154/255, 1
        pos_hint: {"right": 0.97, "y": 0.03}
        on_release: root.go_add_class()
""")


class ClassListScreen(MDScreen):
    """Lists all classes, supports edit and delete operations."""

    name = "class_list"
    _delete_dialog = None
    _error_dialog = None

    def on_pre_enter(self):
        """Refresh class list each time the screen is shown."""
        self.refresh_data()

    def refresh_data(self):
        """Clear the container and rebuild the class list from the database."""
        try:
            self.ids.container.clear_widgets()
            app = App.get_running_app()
            classes = app.db.get_all_classes()

            if not classes:
                self._show_empty_state()
                return

            for cls in classes:
                card = self._build_class_card(cls)
                self.ids.container.add_widget(card)
        except Exception as e:
            self._show_error_dialog("Load Error", f"Failed to load classes: {str(e)}")

    def _show_empty_state(self):
        """Display an empty-state message when no classes are found."""
        try:
            empty_box = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(200),
                spacing=dp(16),
                padding=[dp(16), dp(40), dp(16), dp(16)],
            )
            icon_lbl = MDIcon(
                icon="book-off",
                halign="center",
                font_size="64sp",
                theme_text_color="Custom",
                text_color=(0.6, 0.6, 0.6, 1),
            )
            text_lbl = MDLabel(
                text="No classes found.\nTap + to add one.",
                halign="center",
                font_style="Subtitle1",
                theme_text_color="Secondary",
            )
            empty_box.add_widget(icon_lbl)
            empty_box.add_widget(text_lbl)
            self.ids.container.add_widget(empty_box)
        except Exception as e:
            print(f"[ClassListScreen] _show_empty_state error: {e}")

    def _build_class_card(self, cls: dict) -> MDCard:
        """Build and return a class card widget."""
        try:
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(110),
                radius=[12, 12, 12, 12],
                elevation=1,
                padding=[dp(16), dp(12), dp(16), dp(12)],
                spacing=dp(4),
                md_bg_color=(1, 1, 1, 1),
                ripple_behavior=True,
            )

            # Top row: class name + icon buttons
            top_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(36),
                spacing=dp(8),
            )

            class_icon = MDIcon(
                icon="google-classroom",
                font_size="24sp",
                theme_text_color="Custom",
                text_color=(38/255, 166/255, 154/255, 1),
                size_hint=(None, None),
                size=(dp(28), dp(28)),
            )

            name_lbl = MDLabel(
                text=cls.get("class_name", "Unknown"),
                font_style="Subtitle1",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1),
            )

            cid = cls.get("id")
            cname = cls.get("class_name", "this class")

            edit_btn = MDIconButton(
                icon="pencil",
                theme_text_color="Custom",
                text_color=(63/255, 81/255, 181/255, 0.8),
                size_hint=(None, None),
                size=(dp(36), dp(36)),
            )
            edit_btn.bind(on_release=lambda btn, c_id=cid:
                          self._go_edit_class(c_id))

            delete_btn = MDIconButton(
                icon="delete",
                theme_text_color="Custom",
                text_color=(0.9, 0.1, 0.1, 0.8),
                size_hint=(None, None),
                size=(dp(36), dp(36)),
            )
            delete_btn.bind(on_release=lambda btn, c_id=cid, c_name=cname:
                            self._confirm_delete(c_id, c_name))

            top_row.add_widget(class_icon)
            top_row.add_widget(name_lbl)
            top_row.add_widget(edit_btn)
            top_row.add_widget(delete_btn)

            # Details row
            teacher_lbl = MDLabel(
                text=f"Teacher: {cls.get('teacher_name', 'N/A')}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20),
            )
            fee_lbl = MDLabel(
                text=f"Monthly Fee: Rs. {cls.get('monthly_fee', 0):,.0f}   |   "
                     f"Schedule: {cls.get('schedule', 'N/A') or 'N/A'}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20),
            )

            card.bind(on_release=lambda c, c_id=cid: self._go_edit_class(c_id))
            card.add_widget(top_row)
            card.add_widget(teacher_lbl)
            card.add_widget(fee_lbl)
            return card
        except Exception as e:
            print(f"[ClassListScreen] _build_class_card error: {e}")
            fb = MDCard(size_hint_y=None, height=dp(60))
            fb.add_widget(MDLabel(text="Error loading class", halign="center"))
            return fb

    def _confirm_delete(self, class_id: int, class_name: str):
        """Show a confirmation dialog before deleting a class."""
        try:
            if self._delete_dialog:
                self._delete_dialog.dismiss()
            self._delete_dialog = MDDialog(
                title="Delete Class",
                text=f"Are you sure you want to delete\n[b]{class_name}[/b]?\n"
                     "Students assigned to this class will lose their class assignment.",
                markup=True,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self._delete_dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="DELETE",
                        md_bg_color=(244/255, 67/255, 54/255, 1),
                        on_release=lambda x, cid=class_id: self._do_delete(cid)
                    ),
                ]
            )
            self._delete_dialog.open()
        except Exception as e:
            self._show_error_dialog("Error", f"Could not open dialog: {str(e)}")

    def _do_delete(self, class_id: int):
        """Perform the class deletion and refresh the list."""
        try:
            if self._delete_dialog:
                self._delete_dialog.dismiss()
            app = App.get_running_app()
            success = app.db.delete_class(class_id)
            if success:
                Snackbar(text="Class deleted successfully.").open()
                self.refresh_data()
            else:
                self._show_error_dialog("Error", "Failed to delete class. Please try again.")
        except Exception as e:
            self._show_error_dialog("Delete Error", f"Unexpected error: {str(e)}")

    def _go_edit_class(self, class_id: int):
        """Navigate to the Add/Edit class screen in edit mode."""
        try:
            app = App.get_running_app()
            app.current_class_id = class_id
            self.manager.current = "add_class"
        except Exception as e:
            self._show_error_dialog("Navigation Error", str(e))

    def go_add_class(self):
        """Navigate to the Add/Edit class screen in add mode."""
        try:
            app = App.get_running_app()
            app.current_class_id = None
            self.manager.current = "add_class"
        except Exception as e:
            self._show_error_dialog("Navigation Error", str(e))

    def go_back(self):
        """Navigate back to the dashboard."""
        try:
            self.manager.current = "dashboard"
        except Exception as e:
            print(f"[ClassListScreen] go_back error: {e}")

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
            print(f"[ClassListScreen] _show_error_dialog failed: {e}")
