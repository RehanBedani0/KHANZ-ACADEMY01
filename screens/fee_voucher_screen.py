# File: screens/fee_voucher_screen.py
"""
Fee Voucher Screen — View fee details and download a PDF voucher.
All KV layout is embedded inline via Builder.load_string().
"""

import os
from pathlib import Path
from datetime import date
from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar


# ---------------------------------------------------------------------------
# Utility: safe PDF save path (Android + desktop)
# ---------------------------------------------------------------------------

def get_pdf_path(filename: str) -> str:
    """
    Return a writable path for saving the PDF voucher.
    Uses app_storage_path() on Android, home directory on desktop.
    """
    try:
        from android.storage import app_storage_path  # noqa — Android only
        base = app_storage_path()
    except ImportError:
        base = os.path.expanduser("~")
    pdf_dir = os.path.join(base, "vouchers")
    Path(pdf_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(pdf_dir, filename)


# ---------------------------------------------------------------------------
# KV Layout
# ---------------------------------------------------------------------------

Builder.load_string("""
<FeeVoucherScreen>:
    name: "fee_voucher"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 245/255, 245/255, 245/255, 1

        MDTopAppBar:
            title: "Fee Voucher"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 2

        ScrollView:

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "16dp"
                spacing: "16dp"

                # ── Voucher Preview Card ─────────────────────────────────
                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    radius: [16, 16, 16, 16]
                    elevation: 2
                    padding: "24dp"
                    spacing: "12dp"
                    md_bg_color: 1, 1, 1, 1

                    # Header
                    MDLabel:
                        text: "KHAN'Z ACADEMY"
                        font_style: "H5"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 63/255, 81/255, 181/255, 1
                        size_hint_y: None
                        height: self.texture_size[1] + dp(4)

                    MDLabel:
                        text: "Official Fee Voucher"
                        font_style: "Subtitle1"
                        halign: "center"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(4)

                    MDBoxLayout:
                        size_hint_y: None
                        height: "2dp"
                        md_bg_color: 63/255, 81/255, 181/255, 0.3

                    # Voucher fields
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "28dp"

                        MDLabel:
                            text: "Voucher No:"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Secondary"
                            size_hint_x: 0.4

                        MDLabel:
                            id: lbl_voucher_no
                            text: "—"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "28dp"

                        MDLabel:
                            text: "Date:"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Secondary"
                            size_hint_x: 0.4

                        MDLabel:
                            id: lbl_date
                            text: "—"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1

                    MDBoxLayout:
                        size_hint_y: None
                        height: "1dp"
                        md_bg_color: 0.85, 0.85, 0.85, 1

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "28dp"

                        MDLabel:
                            text: "Student:"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Secondary"
                            size_hint_x: 0.4

                        MDLabel:
                            id: lbl_student_name
                            text: "—"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "28dp"

                        MDLabel:
                            text: "Class:"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Secondary"
                            size_hint_x: 0.4

                        MDLabel:
                            id: lbl_class_name
                            text: "—"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "28dp"

                        MDLabel:
                            text: "Month/Year:"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Secondary"
                            size_hint_x: 0.4

                        MDLabel:
                            id: lbl_month_year
                            text: "—"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1

                    MDBoxLayout:
                        size_hint_y: None
                        height: "1dp"
                        md_bg_color: 0.85, 0.85, 0.85, 1

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "36dp"

                        MDLabel:
                            text: "Amount:"
                            font_style: "Subtitle1"
                            bold: True
                            theme_text_color: "Secondary"
                            size_hint_x: 0.4

                        MDLabel:
                            id: lbl_amount
                            text: "Rs. 0"
                            font_style: "H6"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 63/255, 81/255, 181/255, 1

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "28dp"

                        MDLabel:
                            text: "Status:"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Secondary"
                            size_hint_x: 0.4

                        MDLabel:
                            id: lbl_status
                            text: "Pending"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 255/255, 152/255, 0/255, 1

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "28dp"

                        MDLabel:
                            text: "Paid Date:"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Secondary"
                            size_hint_x: 0.4

                        MDLabel:
                            id: lbl_paid_date
                            text: "—"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1

                    MDBoxLayout:
                        size_hint_y: None
                        height: "2dp"
                        md_bg_color: 63/255, 81/255, 181/255, 0.3

                    MDLabel:
                        text: "Thank you for your payment!"
                        font_style: "Caption"
                        halign: "center"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(8)

                # ── Voucher path label ───────────────────────────────────
                MDLabel:
                    id: lbl_saved_path
                    text: ""
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 76/255, 175/255, 80/255, 1
                    size_hint_y: None
                    height: self.texture_size[1] + dp(4)

                # ── Download Button ──────────────────────────────────────
                MDRaisedButton:
                    id: download_btn
                    text: "DOWNLOAD PDF VOUCHER"
                    size_hint_x: 1
                    size_hint_y: None
                    height: "52dp"
                    icon: "file-pdf-box"
                    md_bg_color: 63/255, 81/255, 181/255, 1
                    on_release: root.generate_pdf()

                Widget:
                    size_hint_y: None
                    height: "16dp"
""")


# ---------------------------------------------------------------------------
# Screen class
# ---------------------------------------------------------------------------

class FeeVoucherScreen(MDScreen):
    """Displays fee voucher details and generates a downloadable PDF."""

    name = "fee_voucher"
    _fee_data = None
    _error_dialog = None
    _success_dialog = None

    def on_pre_enter(self):
        """Load the fee record when the screen is entered."""
        self.refresh_data()

    def refresh_data(self):
        """Load and display the fee record identified by app.current_fee_id."""
        try:
            app = App.get_running_app()
            fee_id = getattr(app, "current_fee_id", None)

            if not fee_id:
                self._clear_labels()
                return

            fee_data = app.db.get_fee_record_by_id(fee_id)
            if not fee_data:
                self._show_error_dialog(
                    "Error", "Fee record not found. It may have been deleted."
                )
                self._clear_labels()
                return

            self._fee_data = fee_data
            self._populate_labels(fee_data)
        except Exception as e:
            self._show_error_dialog("Load Error", f"Failed to load voucher data: {str(e)}")

    def _clear_labels(self):
        """Reset all voucher label values to placeholders."""
        try:
            self.ids.lbl_voucher_no.text = "—"
            self.ids.lbl_date.text = "—"
            self.ids.lbl_student_name.text = "—"
            self.ids.lbl_class_name.text = "—"
            self.ids.lbl_month_year.text = "—"
            self.ids.lbl_amount.text = "Rs. 0"
            self.ids.lbl_status.text = "—"
            self.ids.lbl_paid_date.text = "—"
            self.ids.lbl_saved_path.text = ""
        except Exception as e:
            print(f"[FeeVoucherScreen] _clear_labels error: {e}")

    def _populate_labels(self, fee_data: dict):
        """Populate all label widgets with fee record data."""
        try:
            fee_id = fee_data.get("id", "N/A")
            status = fee_data.get("status", "Pending")
            paid_date = fee_data.get("paid_date") or "—"
            voucher_path = fee_data.get("voucher_path", "")

            self.ids.lbl_voucher_no.text = f"FV-{fee_id}"
            self.ids.lbl_date.text = paid_date if status == "Paid" else date.today().isoformat()
            self.ids.lbl_student_name.text = fee_data.get("full_name", "Unknown")
            self.ids.lbl_class_name.text = fee_data.get("class_name", "Unknown")
            self.ids.lbl_month_year.text = (
                f"{fee_data.get('month', '')} {fee_data.get('year', '')}"
            )
            self.ids.lbl_amount.text = f"Rs. {fee_data.get('amount', 0):,.0f}"
            self.ids.lbl_status.text = status

            # Status color
            if status == "Paid":
                self.ids.lbl_status.text_color = (76/255, 175/255, 80/255, 1)
            else:
                self.ids.lbl_status.text_color = (255/255, 152/255, 0/255, 1)

            self.ids.lbl_paid_date.text = paid_date

            if voucher_path and os.path.exists(voucher_path):
                self.ids.lbl_saved_path.text = f"Saved: {voucher_path}"
            else:
                self.ids.lbl_saved_path.text = ""
        except Exception as e:
            print(f"[FeeVoucherScreen] _populate_labels error: {e}")

    # ------------------------------------------------------------------
    # PDF Generation
    # ------------------------------------------------------------------

    def generate_pdf(self):
        """Generate and save a PDF fee voucher using fpdf2."""
        try:
            if not self._fee_data:
                self._show_error_dialog("Error", "No fee data loaded. Please go back and try again.")
                return

            fee_data = self._fee_data
            from fpdf import FPDF

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # ── Header ──────────────────────────────────────────────────
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 12, "KHAN'Z ACADEMY", align="C", ln=True)

            pdf.set_font("Helvetica", "", 13)
            pdf.cell(0, 8, "Official Fee Voucher", align="C", ln=True)

            pdf.ln(3)
            pdf.set_draw_color(63, 81, 181)
            pdf.set_line_width(0.8)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

            # ── Voucher metadata ─────────────────────────────────────────
            fee_id = fee_data.get("id", "N/A")
            status = fee_data.get("status", "Pending")
            paid_date = fee_data.get("paid_date") or date.today().isoformat()
            today_str = date.today().isoformat()

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 8, "Voucher No:", ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, f"FV-{fee_id}", ln=True)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 8, "Date:", ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, paid_date if status == "Paid" else today_str, ln=True)

            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.3)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

            # ── Student details ──────────────────────────────────────────
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 8, "Student:", ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, fee_data.get("full_name", "Unknown"), ln=True)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 8, "Class:", ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, fee_data.get("class_name", "Unknown"), ln=True)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 8, "Month/Year:", ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(
                0, 8,
                f"{fee_data.get('month', '')} {fee_data.get('year', '')}",
                ln=True
            )

            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

            # ── Amount & Status ──────────────────────────────────────────
            amount = fee_data.get("amount", 0)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(50, 10, "Amount:", ln=False)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, f"Rs. {amount:,.2f}", ln=True)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 8, "Status:", ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, status, ln=True)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 8, "Paid Date:", ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, paid_date if status == "Paid" else "—", ln=True)

            pdf.ln(6)
            pdf.set_draw_color(63, 81, 181)
            pdf.set_line_width(0.8)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(6)

            # ── Footer ──────────────────────────────────────────────────
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(0, 8, "Thank you for your payment!", align="C", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(
                0, 6,
                "This is a computer-generated voucher and does not require a signature.",
                align="C",
                ln=True
            )

            # ── Save PDF ─────────────────────────────────────────────────
            filename = f"voucher_{fee_id}.pdf"
            save_path = get_pdf_path(filename)
            pdf.output(save_path)

            # Update DB
            app = App.get_running_app()
            app.db.update_voucher_path(fee_id, save_path)

            # Update the on-screen path label
            self.ids.lbl_saved_path.text = f"Saved: {save_path}"

            # Show success dialog
            self._show_success_dialog(
                "PDF Saved",
                f"Fee voucher saved to:\n{save_path}"
            )
        except ImportError:
            self._show_error_dialog(
                "Missing Library",
                "fpdf2 library is not installed.\n"
                "Run: pip install fpdf2"
            )
        except Exception as e:
            self._show_error_dialog(
                "PDF Error",
                f"Failed to generate PDF:\n{str(e)}"
            )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def go_back(self):
        """Navigate back to the fee management screen."""
        try:
            self.manager.current = "fee_management"
        except Exception as e:
            print(f"[FeeVoucherScreen] go_back error: {e}")

    # ------------------------------------------------------------------
    # Dialog helpers
    # ------------------------------------------------------------------

    def _show_success_dialog(self, title: str, message: str):
        """Show a success information dialog."""
        try:
            if self._success_dialog:
                self._success_dialog.dismiss()
            self._success_dialog = MDDialog(
                title=title,
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self._success_dialog.dismiss()
                    )
                ]
            )
            self._success_dialog.open()
        except Exception as e:
            print(f"[FeeVoucherScreen] _show_success_dialog failed: {e}")

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
            print(f"[FeeVoucherScreen] _show_error_dialog failed: {e}")
