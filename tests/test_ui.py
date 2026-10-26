import time
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import pytest
from netwatch_terminal.core.settings import Settings
from netwatch_terminal.core.distributions import DISTRIBUTIONS
from netwatch_terminal.ui.main_window import MainWindow, MODULES


def settle(app,window):
    deadline=time.monotonic()+5
    while (window.busy or any(w.isRunning() for w in window.workers)) and time.monotonic()<deadline:
        app.processEvents(); QTest.qWait(10)
    app.processEvents()


@pytest.fixture
def window(app,tmp_path):
    s=Settings(tmp_path/'settings.json'); s.data['fullscreen']=False; s.data['sound']=False
    w=MainWindow(s, monitoring=False); w.engine.cwd=tmp_path; w.show(); app.processEvents()
    yield w
    w.metrics_timer.stop(); settle(app,w); w.close(); app.processEvents()


def test_navigation(app,window):
    for i in range(len(MODULES)):
        window.buttons[i].click(); assert window.pages.currentIndex()==i
    window.focus_input(); app.processEvents(); assert window.command_input.hasFocus()


def test_profiles(app,window):
    for i,p in enumerate(DISTRIBUTIONS):
        window.distribution.setCurrentIndex(i)
        assert p.slug in window.prompt.text()
        assert p.install in window.syntax.text()


def test_command_ui(app,window,tmp_path):
    window.command_input.setText('mkdir "test space"'); QTest.keyClick(window.command_input,Qt.Key.Key_Return)
    settle(app,window)
    assert (tmp_path/'test space').is_dir()
    assert not window.busy


def test_localization_and_settings(app,window):
    assert 'НАСТРОЙКИ' in window.buttons[7].text()
    window.language_combo.setCurrentIndex(1)
    assert 'SETTINGS' in window.buttons[7].text()
    assert Settings(window.settings.path).data['language']=='en'
    window.history_check.setChecked(True); window.clear_history()
    assert 'commands' not in window.settings.data


def test_minimum_window_size(app,window):
    window.resize(1000,650); app.processEvents()
    assert window.command_input.width()>200
    assert window.output.viewport().height()>100


def test_fullscreen_exit(app,window):
    window.toggle_fullscreen(); assert window.isFullScreen()
    window.leave_fullscreen(); assert not window.isFullScreen()


def test_breach_ui_and_timer(app,window):
    assert len(window.cells)==49 and len(window.target_labels)==3
    for r,c in window.game.solution:
        if window.game.finished:break
        window.game_move(r,c)
    assert window.game.won and not window.game_timer.isActive()
    window.restart_game(); assert not window.game.moves
    window.game_move(*window.game.solution[0])
    window.deadline=time.monotonic()-1; window.tick_game()
    assert window.game.expired and not window.game_timer.isActive()


def test_effect_preferences(app,window):
    window.animations_check.setChecked(False)
    window.sound_check.setChecked(False)
    data=Settings(window.settings.path).data
    assert not data['animations'] and not data['sound']
