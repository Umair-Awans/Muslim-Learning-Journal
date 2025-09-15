from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox
from core_utils import Utilities, ProgressUtils


class ClickableLabel(QLabel):
    leftClicked = pyqtSignal()
    rightClicked = pyqtSignal()

    def __init__(self, text=""):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.pressed_style = ""
        self.normal_style = ""

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftClicked.emit() # type: ignore
            if self.pressed_style:
                self.setStyleSheet(self.pressed_style)
                QTimer.singleShot(1000, self.resetStyle)
        elif event.button() == Qt.RightButton:
            self.rightClicked.emit() # type: ignore

    def setPressedStyle(self, style: str):
        self.normal_style = self.styleSheet()
        self.pressed_style = style

    def resetStyle(self):
        if self.normal_style:
            self.setStyleSheet(self.normal_style)


class StyleUtilities:
    @staticmethod
    def get_gradient(hover: bool, title: bool = False) -> str:
        if title:
            top_color = "#E6E6E6" if not hover else "#F2F2F2"
            bottom_color = "#BFBFBF" if not hover else "#D9D9D9"
        else:
            top_color = "#D9D9D9" if not hover else "#E6E6E6"
            bottom_color = "#BFBFBF" if not hover else "#CCCCCC"

        return f"""qlineargradient(
            spread:pad,
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {top_color},
            stop:1 {bottom_color});"""

    @classmethod
    def styleWidgets(cls, *widgets):
        for widget in widgets:
            is_clickable = isinstance(widget, ClickableLabel)

            FONT = 'Fira code' if is_clickable else 'Segoe Script'
            FONT_SIZE = 30 if is_clickable else 35
            # FONT_COLOR = "#2077ce" if is_clickable else "darkblue"
            FONT_COLOR = "#333333"
            BG_COLOR = cls.get_gradient(False) if is_clickable else cls.get_gradient(False, True)

            normal_style = f"""QLabel{{
            border-radius: 5px;
            font-weight: 500;
            color: {FONT_COLOR};
            background: {BG_COLOR};
            font-size: {FONT_SIZE}px;
            font-family: {FONT}, Tahoma;
            padding: 10px;
            qproperty-alignment: 'AlignCenter';
            }}
            ClickableLabel:hover{{
            background: {cls.get_gradient(True)};
            }}"""

            pressed_style = f"""
                border-radius: 5px;
                font-weight: 500;
                color: #333333;
                background: {BG_COLOR};
                font-size: {FONT_SIZE}px;
                font-family: {FONT}, Tahoma;
                padding: 10px;
            """

            widget.setStyleSheet(normal_style)
            if is_clickable:
                widget.setPressedStyle(pressed_style)

    @staticmethod
    def styleFormElements(form_widget):
        form_widget.setStyleSheet("""
            QLineEdit, QTextEdit, QComboBox, QLabel {
                font-size: 25px;
                font-family: consolas;
                min-height: 40px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: white;
            }
            QTextEdit {
                min-height: 100px;
            }
            QLabel, QLineEdit {
                qproperty-alignment: 'AlignCenter';
            }
        """)
    
    @staticmethod
    def applyGlobalStyles(app):
        app.setStyleSheet("""
        QTextBrowser, QRadioButton{
            color: #333333;
            font-size: 25px;
            font-family: 'Tahoma';
        }
        QTextBrowser{
            font-size: 20px;
        }
        QTabBar{
            font-size: 12pt; font-family: Fira code;
        }
        QMainWindow{ 
            background-color: #F2F2F2;
        }
        QDateEdit{ 
            min-height: 50px;
            max-width: 250px;
            font-size: 30px;
            qproperty-alignment: 'AlignCenter';
        }
        """)


class GuiUtilities:
    @staticmethod
    def show_information_msg(parent_widget, message: str):
        QMessageBox.information(parent_widget, 'Muslim Learning Journal',
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)

    @staticmethod
    def show_warning_msg(parent_widget, message: str):
        QMessageBox.warning(parent_widget, 'Muslim Learning Journal',
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)
        
    @staticmethod
    def show_critical_msg(parent_widget, message: str):
        QMessageBox.critical(parent_widget, 'Muslim Learning Journal',
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)

    @staticmethod
    def get_answer(parent_widget, question: str, title: str = "Muslim Learning Journal") -> bool:
        return QMessageBox.question(parent_widget, title,
                                    question,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes # type: ignore

                                    
class FormValidation:
    @staticmethod
    def both_fields_empty(field_name: str, field1, field2):
        if not field1 and not field2:
            return False, f"Can't leave {field_name} fields empty."
        return True, ""

    @staticmethod
    def are_fields_in_order(field_name: str, field1, field2):
        if field1 and field2 and not field1 <= field2:
            return False, f"{field_name}: 'From' field must be smaller than 'To' field"
        return True, ""

    @classmethod
    def verify_range_fields(cls, field_name: str, field1, field2):
        valid, msg = cls.both_fields_empty(field_name, field1, field2)
        if not valid:
            return False, msg
        return cls.are_fields_in_order(field_name, field1, field2)

    @classmethod
    def validate_pair_fields(cls, pair_fields: list):
        for field_name, field1, field2 in pair_fields:
            ok, msg = cls.verify_range_fields(field_name, field1, field2)
            if not ok:
                return False, msg
        return True, ""


class DataProcessor:
    @staticmethod
    def stoi(data: dict):
        for key in data.keys():
            if not "from" in key and not "to" in key:
                continue
            data[key] = float(data[key] or "0")
            if data[key] == int(data[key]):
                data[key] = int(data[key])    

    @staticmethod
    def finalize_common_data(book: str, carrier):
        page_from = carrier.common_raw_data["page_from"]
        page_to = carrier.common_raw_data["page_to"]
        hours = carrier.common_raw_data["hours"]
        minutes = carrier.common_raw_data["minutes"]
        notes = carrier.common_raw_data["notes"].rstrip() or "N/A"
        reading_mode = "Sequential" if carrier.common_raw_data["reading_mode"] else "Random"
        revision = carrier.common_raw_data["revision"].rstrip() or "No"
        pages, total_pages = ProgressUtils.get_str_and_total(page_from, page_to)
        time_spent = Utilities.get_time_str(hours, minutes)
        carrier.common_data = {
                "book": book,
                "pages": pages,
                "total_pages": total_pages,
                "time_spent": time_spent,
                "notes": notes,
                "reading_mode": reading_mode,
                "revision": revision
            }
        return True

    @classmethod
    def process_common_data(cls, carrier):
        cls.stoi(carrier.common_raw_data)
        valid, msg = FormValidation.validate_pair_fields([("Page", carrier.common_raw_data["page_from"], carrier.common_raw_data["page_to"])])
        if not valid:
            return False, msg
        return FormValidation.both_fields_empty("Time Spent", carrier.common_raw_data["hours"], carrier.common_raw_data["minutes"])

    @classmethod
    def finalize_Quran_data(cls, carrier):
        Para = ProgressUtils.get_str_and_total(carrier.raw_data["Para_from"], carrier.raw_data["Para_to"])[0]
        Ruku, total_Ruku = ProgressUtils.get_str_and_total(carrier.raw_data["Ruku_from"], carrier.raw_data["Ruku_to"])
        Para = f"Para no. {Para}"
        carrier.data = {"Ruku": Ruku, "total_Ruku": total_Ruku}
        if "Surah_from" in carrier.raw_data:
            Surah_from = carrier.raw_data["Surah_from"]
            Surah_to = carrier.raw_data["Surah_to"]
            Ayah_from = carrier.raw_data["Ayah_from"]
            Ayah_to = carrier.raw_data["Ayah_to"]
            carrier.data["Surah_number"] = ProgressUtils.get_str_and_total(Surah_from, Surah_to)[0]
            carrier.data["Ayah"], carrier.data["total_Aayat"] = ProgressUtils.get_str_and_total(Ayah_from, Ayah_to)
        return cls.finalize_common_data(Para, carrier)

    @classmethod
    def process_Quran_data(cls, carrier):
        cls.stoi(carrier.raw_data)
        pairs = []
        pairs.append(("Para", carrier.raw_data["Para_from"], carrier.raw_data["Para_to"]))
        if "Surah_from" in carrier.raw_data:
            pairs.append(("Surah", carrier.raw_data["Surah_from"], carrier.raw_data["Surah_to"]))
            pairs.append(("Ayah", carrier.raw_data["Ayah_from"], carrier.raw_data["Ayah_to"]))
        pairs.append(("Ruku", carrier.raw_data["Ruku_from"], carrier.raw_data["Ruku_to"]))
        valid, msg = FormValidation.validate_pair_fields(pairs)
        if not valid:
            return False, msg
        valid, msg = cls.process_common_data(carrier)
        if not valid:
            return False, msg
        return cls.finalize_Quran_data(carrier), "Failed to save data"

    @classmethod
    def finalize_other_data(cls, carrier):
        subject = carrier.raw_data["subject"].strip()
        book = carrier.raw_data["book"].strip()

        if not subject or not book:
            return False, "Can't leave Subject or Book field empty"

        carrier.data["unit"] = ProgressUtils.get_str_and_total(carrier.raw_data["unit_from"], carrier.raw_data["unit_to"])[0]
        carrier.data["chapter"] = carrier.raw_data["chapter"].strip() or "N/A"
        return cls.finalize_common_data(book, carrier)

    @classmethod
    def process_other_data(cls, carrier):
        cls.stoi(carrier.raw_data)
        pairs = [("Unit", carrier.raw_data["unit_from"], carrier.raw_data["unit_to"])]
        valid, msg = FormValidation.validate_pair_fields(pairs)
        if not valid:
            return False, msg
        valid, msg = cls.process_common_data(carrier)
        if not valid:
            return False, msg
        return cls.finalize_other_data(carrier), "Failed to save data"


class GuiDataCollector:
    @staticmethod
    def collect_common_raw_data(form, carrier):
        carrier.common_raw_data = form.collect_common_raw_input()

    @classmethod
    def collect_raw_data(cls, form, carrier):
        cls.collect_common_raw_data(form, carrier)
        carrier.raw_data = form.collect_raw_input()

    @classmethod
    def collect_Quran_data(cls, carrier, args: dict):
        form = args["form"]
        cls.collect_raw_data(form, carrier)
        return DataProcessor.process_Quran_data(carrier)

    @classmethod
    def collect_other_data(cls, carrier, args: dict):
        form = args["form"]
        cls.collect_raw_data(form, carrier)
        return DataProcessor.process_other_data(carrier)
