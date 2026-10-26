import os
from pathlib import Path
from unittest.mock import patch
import pytest
from netwatch_terminal.core.engine import Engine,parse
from netwatch_terminal.core.settings import Settings
from netwatch_terminal.core.breach import Puzzle


def test_parser():
    assert parse(r'cat "C:\My Files\hello.txt"')==['cat',r'C:\My Files\hello.txt']
    assert parse("echo ''")==['echo','']
    for line in ('ls | cat','rm a; pwd','echo $(pwd)','cat > output','cat "oops'):
        with pytest.raises(ValueError): parse(line)


def test_files(tmp_path):
    e=Engine(tmp_path)
    assert e.execute('mkdir "hello world"').success
    assert e.execute('cd "hello world"').success
    assert e.cwd==tmp_path/'hello world'
    (e.cwd/'a.txt').write_text('hello\nworld\nworld\n',encoding='utf-8')
    assert e.execute('grep world a.txt').output=='world\nworld'
    assert e.execute('head -n 1 a.txt').output=='hello'
    assert e.execute('tail -n 0 a.txt').output==''
    assert e.execute('uniq a.txt').output=='hello\nworld'
    assert e.execute('cp a.txt b.txt').success
    assert not e.execute('cp a.txt b.txt').success
    assert e.execute('mv b.txt c.txt').success
    assert not (e.cwd/'b.txt').exists()
    result=e.execute('rm c.txt'); assert result.confirmation and (e.cwd/'c.txt').exists()
    assert e.execute('rm c.txt',True).success
    assert not (e.cwd/'c.txt').exists()
    assert not e.execute('rm -rf .',True).success
    assert not e.execute('rm .',True).success
    assert not e.execute('cat missing').success
    assert not e.execute('ls -z').success


def test_bounded_read_and_unknown(tmp_path):
    (tmp_path/'large').write_bytes(b'x'*(1024*1024+1))
    e=Engine(tmp_path)
    assert not e.execute('cat large').success
    assert not e.execute('arbitrary_untrusted_command').success
    assert e.execute('translate mkdir demo').success
    assert not (tmp_path/'demo').exists()


def test_launch_confirmation(tmp_path):
    e=Engine(tmp_path); app=tmp_path/'demo.exe'; app.touch()
    with patch('netwatch_terminal.core.engine.subprocess.Popen') as launch:
        launch.return_value.pid=123
        assert e.execute(f'run "{app}"').confirmation
        launch.assert_not_called()
        assert e.execute(f'run "{app}" argument',True).success
        assert launch.call_args.kwargs['shell'] is False
        assert launch.call_args.args[0]==[str(app),'argument']


def test_kill_is_guarded(tmp_path):
    e=Engine(tmp_path)
    assert e.execute(f'kill {os.getpid()}').confirmation
    assert not e.execute(f'kill {os.getpid()}',True).success


def test_settings(tmp_path):
    p=tmp_path/'settings.json'; s=Settings(p)
    assert s.data['language']=='ru' and not s.data['history']
    s.data['profile']=3; s.save(); assert Settings(p).data['profile']==3
    p.write_text('broken'); assert Settings(p).data['language']=='ru'


def test_puzzle():
    for seed in range(100):
        p=Puzzle(seed)
        assert not p.allowed(1,0)
        for r,c in p.solution:
            if p.finished: break
            assert p.allowed(r,c); p.choose(r,c)
        assert p.won
        with pytest.raises(ValueError): p.choose(*p.moves[0])
    assert Puzzle(2).grid==Puzzle(2).grid


def test_startup_toggle_without_touching_registry(monkeypatch):
    import sys
    from types import SimpleNamespace
    from unittest.mock import MagicMock
    import netwatch_terminal.core.settings as settings
    registry=MagicMock(); registry.HKEY_CURRENT_USER=1; registry.REG_SZ=1
    monkeypatch.setitem(sys.modules,'winreg',registry)
    monkeypatch.setattr(settings,'os',SimpleNamespace(name='nt'))
    settings.set_startup(True)
    args=registry.SetValueEx.call_args.args
    assert args[1]=='NetwatchTerminal' and 'netwatch_terminal' in args[-1]
    settings.set_startup(False)
    assert registry.DeleteValue.call_args.args[1]=='NetwatchTerminal'


def test_short_program_names(tmp_path,monkeypatch):
    from netwatch_terminal.core.programs import resolve_program
    import netwatch_terminal.core.programs as programs
    monkeypatch.setattr(programs,'registered_paths',lambda name:[])
    monkeypatch.setattr(programs.shutil,'which',lambda name:None)
    root=tmp_path/'Programs'; steam=root/'Steam'/'steam.exe'; steam.parent.mkdir(parents=True); steam.touch()
    monkeypatch.setenv('ProgramFiles(x86)',str(root))
    assert resolve_program('steam',tmp_path)==steam.resolve()
    assert resolve_program('STEAM.EXE',tmp_path)==steam.resolve()
    app=tmp_path/'custom.exe'; app.touch()
    assert resolve_program('custom',tmp_path,[str(app)])==app.resolve()
    registered=tmp_path/'registered.exe'; registered.touch()
    monkeypatch.setattr(programs,'registered_paths',lambda name:[registered])
    assert resolve_program('registered',tmp_path)==registered.resolve()
    monkeypatch.setattr(programs,'registered_paths',lambda name:[])
    with pytest.raises(FileNotFoundError):resolve_program('nonexistent_app_xyz',tmp_path)


def test_multi_target_expiry():
    p=Puzzle(22); p.expired=True
    assert p.finished and not p.allowed(0,0)
    p.restart(); assert not p.finished and not p.moves
    for r,c in p.solution:
        if p.finished:break
        p.choose(r,c)
    assert p.won and all(p.completed)
