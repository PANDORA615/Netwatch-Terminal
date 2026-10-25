from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from netwatch_terminal import __version__
from netwatch_terminal.core.distributions import DISTRIBUTIONS
from netwatch_terminal.ui.main_window import MODULES, MainWindow


def test_import():
    assert __version__ == "0.1.0"


def test_navigation_and_keyboard(app):
    window = MainWindow()
    window.show()
    app.processEvents()
    for index in range(len(MODULES)):
        window.buttons[index].click()
        assert window.pages.currentIndex() == index
        assert window.buttons[index].isChecked()
    window.focus_input()
    app.processEvents()
    assert window.pages.currentIndex() == 1
    assert window.command_input.hasFocus()
    window.close()


def test_every_profile_updates_reference(app):
    window = MainWindow()
    for index, profile in enumerate(DISTRIBUTIONS):
        window.distribution.setCurrentIndex(index)
        assert profile.slug in window.prompt.text()
        assert profile.install in window.syntax.text()
        assert profile.search in window.syntax.text()
        assert profile.shell.upper() in window.profile_info.text()
        assert "Commands are not executed" in window.output.toPlainText()
    window.close()


def test_preview_does_not_execute_or_retain_input(app, tmp_path):
    window = MainWindow()
    target = tmp_path / "must-not-exist"
    entered = f'mkdir "{target}"'
    window.command_input.setText(entered)
    QTest.keyClick(window.command_input, Qt.Key.Key_Return)
    assert not target.exists()
    assert not window.command_input.text()
    assert entered not in window.output.toPlainText()
    assert "Input received" in window.output.toPlainText()
    window.close()


def test_minimum_window_size(app):
    window = MainWindow()
    window.resize(1000, 650)
    window.show()
    app.processEvents()
    assert window.command_input.isVisible()
    assert window.command_input.width() > 200
    assert window.output.viewport().height() > 100
    window.close()
