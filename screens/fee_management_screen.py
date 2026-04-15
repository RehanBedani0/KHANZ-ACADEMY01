# File: screens/fee_management_screen.py
"""
Fee Management Screen — Generate monthly fees, view status, and mark payments.
All KV layout is embedded inline via Builder.load_string().
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from datetime import date, datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import TwoLineListItem, MDList
from kivymd.uix.label import MDIcon

# Month names
MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December",
]

Builder.load_string("""
<FeeManagementScreen>:
    name: "fee_management"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 245/255, 245/255, 245/255, 1

        MDTopAppBar:
            title: "Fee Management"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 2

        ScrollView:

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "12dp"
                spacing: "12dp"

                # ── Control Card ─────────────────────────────────────────
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
                        text: "Select Filters"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 76/255, 175/255, 80/255, 1
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

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "48dp"
                        spacing: "8dp"

                        MDRaisedButton:
                            text: "VIEW FEES"
                            size_hint_x: 1
                            size_hint_y: None
                            height: "48dp"
                            md_bg_color: 63/255, 81/255, 181/255, 1
                            on_release: root.load_fee_records()

                        MDRaisedButton:
                            text: "GENERATE FEES"
                            size_hint_x: 1
                            size_hint_y: None
                            height: "48dp"
                            md_bg_color: 76/255, 175/255, 80/255, 1
                            on_release: root.generate_fees()

                # ── Summary Card ─────────────────────────────────────────
                MDCard:
                    id: summary_card
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "80dp"
                    radius: [12, 12, 12, 12]
                    elevation: 1
                    padding: "16dp"
                    spacing: "16dp"
                    md_bg_color: 1, 1, 1, 1
                    opacity: 0

                    MDBoxLayout:
                        orientation: "vertical"
                        adaptive_height: True

                        MDLabel:
                            id: lbl_collected
                            text: "Collected: Rs. 0"
                            font_style: "Subtitle1"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 76/255, 175/255, 80/255, 1

                        MDLabel:
                            id: lbl_pending_amount
                            text: "Pending: Rs. 0"
                            font_style: "Subtitle2"
                            theme_text_color: "Custom"
                            text_color: 255/255, 152/255, 0/255, 1

                # ── Fee List Container ───────────────────────────────────
                MDBoxLayout:
                    id: fee_container
                    orientation: "vertical"
                    adaptive_height: True
                    spacing: "8dp"

                Widget:
                    size_hint_y: None
                    height: "16dp"
""")


class FeeManagementScreen(MDScreen):
    """Manage fee records — generate, view, mark paid, and open voucher."""

    name = "fee_management"

    _selected_class_id = None
    _selected_class_name = ""
    _class_picker_dialog = None
    _month_picker_dialog = None
    _error_dialog = None
    _confirm_dialog = None

    def on_pre_enter(self):
        """Refresh fee management screen when entered."""
        self.refresh_data()

    def refresh_data(self):
        """Reset filters and clear fee list."""
        try:
            today = datetime.now()
            self._selected_class_id = None
            self._selected_class_name = ""

            self.ids.class_display_field.text = ""
            self.ids.month_display_field.text = MONTHS[today.month - 1]
            self.ids.year_display_field.text = str(today.year)
            self.ids.fee_container.clear_widgets()
            self.ids.summary_card.opacity = 0
        except Exception as e:
            print(f"[FeeManagementScreen] refresh_data error: {e}")

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
                    secondary_text=(
                        f"Teacher: {cls['teacher_name']}  |  "
                        f"Fee: Rs. {cls['monthly_fee']:,.0f}"
                    ),
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
        """Handle class selection."""
        try:
            self._selected_class_id = class_id
            self._selected_class_name = class_name
            self.ids.class_display_field.text = class_name
            if self._class_picker_dialog:
                self._class_picker_dialog.dismiss()
        except Exception as e:
            print(f"[FeeManagementScreen] _select_class error: {e}")

    # ------------------------------------------------------------------
    # Month picker
    # ------------------------------------------------------------------

    def show_month_picker(self):
        """Show a dialog to select a month."""
        try:
            if self._month_picker_dialog:
                self._month_picker_dialog.dismiss()

            list_widget = MDList()
            from kivy.uix.scrollview import ScrollView as KVScrollView
            scroll = KVScrollView(size_hint_y=None, height=dp(300))

            for month_name in MONTHS:
                item = TwoLineListItem(text=month_name, secondary_text="")
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
        """Handle month selection."""
        try:
            self.ids.month_display_field.text = month_name
            if self._month_picker_dialog:
                self._month_picker_dialog.dismiss()
        except Exception as e:
            print(f"[FeeManagementScreen] _select_month error: {e}")

    # ------------------------------------------------------------------
    # Generate fees
    # ------------------------------------------------------------------

    def generate_fees(self):
        """Bulk-generate Pending fee records for all students in the selected class."""
        try:
            if not self._selected_class_id:
                self._show_error_dialog("Error", "Please select a class first.")
                return

            month_name = self.ids.month_display_field.text.strip()
            year_str = self.ids.year_display_field.text.strip()
            if not month_name or not year_str:
                self._show_error_dialog("Error", "Please select a month and year.")
                return

            try:
                year = int(year_str)
            except ValueError:
                self._show_error_dialog("Error", "Year must be a valid number.")
                return

            app = App.get_running_app()
            inserted = app.db.generate_monthly_fees(
                self._selected_class_id, month_name, year
            )

            if inserted > 0:
                Snackbar(
                    text=f"Generated {inserted} fee records for {month_name} {year}."
                ).open()
                self.load_fee_records()
            elif inserted == 0:
                self._show_info_dialog(
                    "Already Generated",
                    f"Fee records for {month_name} {year} already exist "
                    "for all students in this class. No new records were created."
                )
        except Exception as e:
            self._show_error_dialog("Generate Error", f"Failed to generate fees: {str(e)}")

    # ------------------------------------------------------------------
    # Load / display fee records
    # ------------------------------------------------------------------

    def load_fee_records(self):
        """Fetch and display fee records for the selected class/month/year."""
        try:
            if not self._selected_class_id:
                self._show_error_dialog("Error", "Please select a class first.")
                return

            month_name = self.ids.month_display_field.text.strip()
            year_str = self.ids.year_display_field.text.strip()
            if not month_name or not year_str:
                self._show_error_dialog("Error", "Please select a month and year.")
                return

            try:
                year = int(year_str)
            except ValueError:
                self._show_error_dialog("Error", "Year must be a valid number.")
                return

            app = App.get_running_app()
            records = app.db.get_fee_records(
                self._selected_class_id, month_name, year
            )

            self.ids.fee_container.clear_widgets()

            if not records:
                self.ids.summary_card.opacity = 0
                self.ids.fee_container.add_widget(
                    MDLabel(
                        text=f"No fee records for {month_name} {year}.\n"
                             "Tap 'GENERATE FEES' to create them.",
                        halign="center",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(80),
                    )
                )
                return

            # Compute summary
            collected = sum(r["amount"] for r in records if r["status"] == "Paid")
            pending = sum(r["amount"] for r in records if r["status"] == "Pending")
            self.ids.lbl_collected.text = f"Collected: Rs. {collected:,.0f}"
            self.ids.lbl_pending_amount.text = f"Pending: Rs. {pending:,.0f}"
            self.ids.summary_card.opacity = 1

            for rec in records:
                card = self._build_fee_card(rec)
                self.ids.fee_container.add_widget(card)
        except Exception as e:
            self._show_error_dialog("Load Error", f"Failed to load fee records: {str(e)}")

    def _build_fee_card(self, rec: dict) -> MDCard:
        """Build and return a fee record card widget."""
        try:
            is_paid = rec.get("status") == "Paid"
            status_color = (
                (76/255, 175/255, 80/255, 1)
                if is_paid
                else (255/255, 152/255, 0/255, 1)
            )

            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100),
                radius=[12, 12, 12, 12],
                elevation=1,
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(4),
                md_bg_color=(1, 1, 1, 1),
            )

            # Top row: name + status badge
            top_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30),
            )
            name_lbl = MDLabel(
                text=rec.get("full_name", "Unknown"),
                font_style="Subtitle1",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1),
            )
            status_lbl = MDLabel(
                text=rec.get("status", "Pending"),
                font_style="Caption",
                bold=True,
                halign="right",
                theme_text_color="Custom",
                text_color=status_color,
                size_hint_x=0.3,
            )
            top_row.add_widget(name_lbl)
            top_row.add_widget(status_lbl)

            # Amount row
            amount_lbl = MDLabel(
                text=(
                    f"Amount: Rs. {rec.get('amount', 0):,.0f}   |   "
                    f"Month: {rec.get('month', '')} {rec.get('year', '')}"
                ),
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20),
            )

            # Action buttons row
            btn_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(36),
                spacing=dp(8),
            )

            fee_id = rec.get("id")

            if not is_paid:
                mark_paid_btn = MDRaisedButton(
                    text="MARK PAID",
                    size_hint_y=None,
                    height=dp(32),
                    md_bg_color=(76/255, 175/255, 80/255, 1),
                )
                mark_paid_btn.bind(
                    on_release=lambda btn, fid=fee_id: self._do_mark_paid(fid)
                )
                btn_row.add_widget(mark_paid_btn)

            voucher_btn = MDIconButton(
                icon="receipt",
                theme_text_color="Custom",
                text_color=(63/255, 81/255, 181/255, 1),
                size_hint=(None, None),
                size=(dp(36), dp(36)),
            )
            voucher_btn.bind(
                on_release=lambda btn, fid=fee_id: self._go_voucher(fid)
            )
            btn_row.add_widget(voucher_btn)

            card.add_widget(top_row)
            card.add_widget(amount_lbl)
            card.add_widget(btn_row)
            return card
        except Exception as e:
            print(f"[FeeManagementScreen] _build_fee_card error: {e}")
            fb = MDCard(size_hint_y=None, height=dp(60))
            fb.add_widget(MDLabel(text="Error loading fee record", halign="center"))
            return fb

    def _do_mark_paid(self, fee_id: int):
        """Mark a fee record as paid and refresh the list."""
        try:
            app = App.get_running_app()
            success = app.db.mark_fee_paid(fee_id)
            if success:
                Snackbar(text="Fee marked as Paid!").open()
                self.load_fee_records()
            else:
                self._show_error_dialog("Error", "Failed to mark fee as paid. Please try again.")
        except Exception as e:
            self._show_error_dialog("Error", f"Unexpected error: {str(e)}")

    def _go_voucher(self, fee_id: int):
        """Navigate to the fee voucher screen for a specific fee record."""
        try:
            app = App.get_running_app()
            app.current_fee_id = fee_id
            self.manager.current = "fee_voucher"
        except Exception as e:
            self._show_error_dialog("Navigation Error", str(e))

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def go_back(self):
        """Navigate back to the dashboard."""
        try:
            self.manager.current = "dashboard"
        except Exception as e:
            print(f"[FeeManagementScreen] go_back error: {e}")

    def _show_info_dialog(self, title: str, message: str):
        """Show an informational dialog."""
        self._show_error_dialog(title, message)

    def _show_error_dialog(self, title: str, message: str):
        """Show a modal error/info dialog."""
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
            print(f"[FeeManagementScreen] _show_error_dialog failed: {e}")
