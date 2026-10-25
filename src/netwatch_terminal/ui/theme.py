STYLESHEET = """
QWidget { background: #0B0E12; color: #E7E9ED; font-size: 13px; }
QLabel { background: transparent; }
QLabel#muted { color: #85919F; }
QLabel#accent { color: #F0CB56; }
QLabel#title { font-size: 29px; font-weight: bold; }
QLabel#brand { font-size: 22px; font-weight: bold; color: #F0CB56; }
QFrame#sidebar { background: #10151C; border-right: 1px solid #28313D; }
QFrame#panel { background: #151B22; border: 1px solid #2A3440; border-radius: 5px; }
QFrame#panel QLabel, QFrame#panel QCheckBox { background: transparent; }
QPushButton { text-align: left; padding: 12px; border: 1px solid #303B48; border-radius: 3px; background: #151B22; }
QPushButton:hover { border-color: #F0CB56; color: #F0CB56; }
QPushButton:checked { background: #302C1B; color: #F0CB56; border-left: 3px solid #F0CB56; }
QPushButton:focus, QLineEdit:focus, QComboBox:focus, QCheckBox:focus { border: 2px solid #F0CB56; }
QComboBox { padding: 10px; background: #1C242E; border: 1px solid #596473; border-radius: 3px; min-width: 150px; }
QComboBox QAbstractItemView { background: #151B22; selection-background-color: #403A23; }
QLineEdit { padding: 13px; background: #10151C; border: 1px solid #4B5664; selection-background-color: #695921; }
QPlainTextEdit { padding: 18px; border: none; background: #0D1218; color: #BAC7D5; selection-background-color: #554B27; }
QScrollArea { border: none; }
QScrollBar:vertical { background: #10151C; width: 10px; }
QScrollBar::handle:vertical { background: #3A4655; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QStatusBar { color: #85919F; border-top: 1px solid #28313D; }
QToolTip { background: #151B22; color: #F0CB56; border: 1px solid #F0CB56; }
"""
