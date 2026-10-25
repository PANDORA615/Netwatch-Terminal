"""Original phosphor HUD palette, inspired by industrial terminal displays."""

STYLESHEET = """
QWidget { background: transparent; color: #D4DBB4; font-size: 13px; }
QMainWindow { background: #100F19; }
QLabel { background: transparent; }
QLabel#muted { color: #92977E; }
QLabel#accent { color: #DCFA63; }
QLabel#title { font-size: 32px; font-weight: bold; color: #E4F6AA; letter-spacing: 2px; }
QLabel#brand { font-size: 23px; font-weight: bold; color: #DCFA63; letter-spacing: 1px; }
QLabel#ribbon { background: #DCFA63; color: #171C0D; padding: 7px 12px; font-weight: bold; letter-spacing: 1px; }
QLabel#section { background: #CADF64; color: #171C0D; padding: 9px 12px; font-weight: bold; }
QLabel#readout { color: #DCFA63; background: #22251B; border: 1px solid #636B3E; padding: 8px 10px; font-size: 11px; }
QFrame#sidebar { background: #11121A; border-right: 1px solid #636B3E; }
QFrame#panel { background: #12131E; border: 1px solid #616641; border-radius: 0px; }
QFrame#panel QLabel, QFrame#panel QCheckBox { background: transparent; }
QFrame#panel QLabel#section { background: #DCFA63; color: #171C0D; }
QPushButton { text-align: left; padding: 12px; border: 1px solid #434A33; border-radius: 0px; background: #15171C; color: #B5C28D; }
QPushButton:hover { border-color: #DCFA63; background: #252B1D; color: #F0FFAA; }
QPushButton:checked { background: #DCFA63; color: #171C0D; border: 1px solid #DCFA63; font-weight: bold; }
QPushButton:focus, QLineEdit:focus, QComboBox:focus, QCheckBox:focus { border: 2px solid #DCFA63; }
QComboBox { padding: 10px; background: #22251B; color: #E3F0BB; border: 1px solid #869451; border-radius: 0px; min-width: 150px; }
QComboBox QAbstractItemView { background: #171B1A; color: #E3F0BB; selection-background-color: #DCFA63; selection-color: #171C0D; }
QLineEdit { padding: 13px; background: #12151B; border: 1px solid #869451; color: #E6F7BA; selection-background-color: #52652A; }
QPlainTextEdit { padding: 18px; border: none; background: #11121C; color: #C7D49F; selection-background-color: #52652A; }
QScrollArea { border: none; }
QScrollBar:vertical { background: #11121C; width: 8px; }
QScrollBar::handle:vertical { background: #7D8A49; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QStatusBar { background: #15191C; color: #A0C5BC; border-top: 1px solid #636B3E; padding: 4px; }
QToolTip { background: #20251A; color: #DCFA63; border: 1px solid #DCFA63; }
"""
