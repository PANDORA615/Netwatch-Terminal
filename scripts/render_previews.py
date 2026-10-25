"""Render the actual Qt views for the README (no mock UI or telemetry)."""

import os
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from netwatch_terminal.app import create_application
from netwatch_terminal.ui.main_window import MainWindow


def main():
    app = create_application([])
    window = MainWindow()
    window.show()
    output = Path(__file__).resolve().parents[1] / 'docs'
    output.mkdir(exist_ok=True)
    for filename, page, profile in (
        ('terminal-preview.png', 1, 0),
        ('dashboard-preview.png', 0, 0),
        ('arch-preview.png', 1, 3),
    ):
        window.distribution.setCurrentIndex(profile)
        window.navigate(page)
        if page == 1:
            window.command_input.setFocus()
        app.processEvents()
        if not window.grab().save(str(output / filename)):
            raise RuntimeError(f'Could not render {filename}')
    window.close()


if __name__ == '__main__':
    main()
