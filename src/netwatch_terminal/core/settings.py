"""User settings and opt-in Windows startup; no administrator rights needed."""
import json
import os
from pathlib import Path
import subprocess
import sys
from platformdirs import user_config_path


def config_path():
    return user_config_path('NetwatchTerminal', appauthor=False) / 'settings.json'


class Settings:
    def __init__(self, path=None):
        self.path = Path(path) if path else config_path()
        self.data = dict(language='ru', fullscreen=True, history=False, profile=0, favorites=[])
        try:
            values = json.loads(self.path.read_text(encoding='utf-8'))
            if isinstance(values, dict):
                self.data.update(values)
        except (OSError, ValueError):
            pass
        if self.data.get('language') not in ('ru','en'): self.data['language']='ru'
        if not isinstance(self.data.get('profile'),int): self.data['profile']=0
        for key in ('fullscreen','history'):
            if not isinstance(self.data.get(key),bool): self.data[key]=(key=='fullscreen')
        for key in ('favorites','commands'):
            values=self.data.get(key,[])
            self.data[key]=[v for v in values if isinstance(v,str)][:200] if isinstance(values,list) else []
        if not isinstance(self.data.get('best',7),int): self.data.pop('best',None)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')
        temp.replace(self.path)


def startup_enabled():
    if os.name != 'nt':
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
            return bool(winreg.QueryValueEx(key, 'NetwatchTerminal')[0])
    except OSError:
        return False


def set_startup(enabled):
    if os.name != 'nt':
        raise OSError('Windows only / Только для Windows')
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
        if enabled:
            args = [sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, '-m', 'netwatch_terminal']
            winreg.SetValueEx(key, 'NetwatchTerminal', 0, winreg.REG_SZ, subprocess.list2cmdline(args))
        else:
            try:
                winreg.DeleteValue(key, 'NetwatchTerminal')
            except FileNotFoundError:
                pass
