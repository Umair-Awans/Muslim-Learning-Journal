from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from gui.styles import StyleSheets


class BaseScreen(QWidget):

    def __init__(self, title: str, content_widget, back_label, parent=None):
        super().__init__(parent)

        self.title = QLabel(title)
        self.title.setStyleSheet(StyleSheets.label_normal())

        self.screen_layout = QVBoxLayout(self)
        self.screen_layout.addWidget(self.title)
        self.screen_layout.addWidget(content_widget)
        self.screen_layout.addWidget(back_label)