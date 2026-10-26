"""Render the actual Qt views for the README (no mock UI or telemetry)."""

import os
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import tempfile
from netwatch_terminal.core.settings import Settings
from netwatch_terminal.app import create_application
from netwatch_terminal.ui.main_window import MainWindow


def main():
    app = create_application([])
    temp = tempfile.TemporaryDirectory()
    window = MainWindow(Settings(Path(temp.name) / 'settings.json'))
    window.metrics_timer.stop()
    while any(w.isRunning() for w in window.workers):
        app.processEvents()
    app.processEvents()
    window.show()
    output = Path(__file__).resolve().parents[1] / 'docs'
    output.mkdir(exist_ok=True)
    for filename, page, profile in (
        ('terminal-preview.png', 1, 0),
        ('dashboard-preview.png', 0, 0),
        ('arch-preview.png', 1, 3),
        ('settings-preview.png', 7, 0),
        ('breach-preview.png', 6, 0),
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
