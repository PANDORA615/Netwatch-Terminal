"""Application entry point; importing this module never starts Qt."""

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.theme import STYLESHEET


def create_application(argv=None):
    app = QApplication.instance() or QApplication(argv or [])
    app.setApplicationName("NETWATCH TERMINAL")
    app.setOrganizationName("NetwatchTerminal")
    app.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
    app.setStyleSheet(STYLESHEET)
    return app


def main(argv=None):
    parser = argparse.ArgumentParser(description="NETWATCH desktop interface preview")
    parser.add_argument("--screenshot", type=Path, help="Save a screenshot and exit")
    args = parser.parse_args(argv)
    app = create_application(sys.argv[:1])
    window = MainWindow()
    window.show()
    exit_status = 0
    if args.screenshot:
        def capture():
            nonlocal exit_status
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            if not window.grab().save(str(args.screenshot)):
                exit_status = 1
            app.quit()
        QTimer.singleShot(500, capture)
    result = app.exec()
    return exit_status or result
