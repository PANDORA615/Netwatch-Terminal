"""Resolve explicit program names from Windows registrations and known install locations."""
import os
from pathlib import Path
import shutil


def registered_paths(name):
    if os.name != 'nt': return []
    import winreg
    found=[]
    for root in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
        for view in (winreg.KEY_WOW64_64KEY,winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(root, rf'Software\Microsoft\Windows\CurrentVersion\App Paths\{name}.exe',0,winreg.KEY_READ|view) as key:
                    found.append(Path(winreg.QueryValueEx(key,'')[0].strip('"')))
            except OSError: pass
    if name=='steam':
        for root,key,value in ((winreg.HKEY_CURRENT_USER,r'Software\Valve\Steam','SteamExe'),(winreg.HKEY_LOCAL_MACHINE,r'Software\Valve\Steam','InstallPath')):
            for view in (winreg.KEY_WOW64_32KEY,winreg.KEY_WOW64_64KEY):
                try:
                    with winreg.OpenKey(root,key,0,winreg.KEY_READ|view) as handle:
                        path=Path(winreg.QueryValueEx(handle,value)[0]); found.append(path/'steam.exe' if value=='InstallPath' else path)
                except OSError: pass
    return found


def resolve_program(value,cwd,favorites=()):
    explicit=Path(value).expanduser()
    if explicit.is_absolute() or '/' in value or '\\' in value:
        candidates=[explicit if explicit.is_absolute() else Path(cwd)/explicit]
    else:
        name=value.lower().removesuffix('.exe')
        candidates=[Path(p) for p in favorites if Path(p).stem.lower()==name]
        candidates+=registered_paths(name)
        # Known locations, not a recursive search through the user's disks.
        locations={'steam':['Steam/steam.exe'],'chrome':['Google/Chrome/Application/chrome.exe'],
                   'firefox':['Mozilla Firefox/firefox.exe'],'code':['Microsoft VS Code/Code.exe'],
                   'telegram':['Telegram Desktop/Telegram.exe'],'spotify':['Spotify/Spotify.exe']}
        for variable in ('ProgramFiles(x86)','ProgramFiles','LOCALAPPDATA','APPDATA'):
            root=os.environ.get(variable)
            if root:
                for relative in locations.get(name,[]): candidates.append(Path(root)/relative)
                if variable=='LOCALAPPDATA':
                    for relative in locations.get(name,[]): candidates.append(Path(root)/'Programs'/relative)
                    if name=='discord':
                        candidates+=sorted((Path(root)/'Discord').glob('app-*/Discord.exe'),reverse=True)
        match=shutil.which(value)
        if match: candidates.append(Path(match))
    for candidate in candidates:
        if candidate.is_file() and (os.name!='nt' or candidate.suffix.lower()=='.exe'):
            return candidate.resolve()
    raise FileNotFoundError(f'Program not found / Программа не найдена: {value}. Добавьте её в «Программы» или укажите полный путь.')
