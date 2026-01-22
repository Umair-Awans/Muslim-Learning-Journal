

class StyleSheets:
    @staticmethod
    def gradient(hover: bool, title: bool = False) -> str:
        if title:
            top = "#f9eb9c" if not hover else "gold"
            bottom = "#fbe359" if not hover else "#f9eb9c"
        else:
            top = "#f9eb9c"
            bottom = "gold" if hover else "#fbe359"

        return f"""qlineargradient(
            spread:pad,
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {top},
            stop:1 {bottom});"""

    @staticmethod
    def label_normal() -> str:
        return f"""
        QLabel {{
            border-radius: 5px;
            font-weight: 500;
            color: #1e293b;
            background: {StyleSheets.gradient(False)};
            font-size: 30px;
            font-family: Consolas, Arial;
            padding: 10px;
            qproperty-alignment: 'AlignCenter';
        }}
        ClickableLabel:hover {{
            background: {StyleSheets.gradient(True)};
        }}
        """

    @staticmethod
    def label_pressed() -> str:
        return f"""
        border-radius: 5px;
        font-weight: 500;
        color: #1e293b;
        background: {StyleSheets.gradient(True)};
        font-size: 30px;
        font-family: Consolas, Arial;
        padding: 10px;
        """
    @staticmethod
    def form_style_sheet():
        return ("""
            QLineEdit, QTextEdit, QComboBox, QLabel {
                font-size: 25px;
                font-family: Consolas;
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
    def global_style_sheet():
        return ("""
        QTextBrowser, QRadioButton{
            color: #333333;
            font-size: 25px;
            font-family: 'Consolas';
        }
        QTextBrowser{
            font-size: 20px;
        }
        QTabBar{
            font-size: 12pt; font-family: Consolas;
        }
        QMainWindow{ 
            background-color: #FEFCE8;
        }
        QDateEdit{ 
            min-height: 50px;
            max-width: 250px;
            font-size: 30px;
            qproperty-alignment: 'AlignCenter';
        }        
        """)
