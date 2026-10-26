"""Bounded Linux-style commands implemented using Python APIs, never a shell."""
from dataclasses import dataclass
from datetime import datetime
import getpass
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import time
import psutil

COMMANDS = 'help clear pwd ls cd cat mkdir touch cp mv rm rmdir head tail grep wc sort uniq stat du df basename dirname realpath echo date whoami hostname uname uptime ps kill which env printenv run open translate explain preview history breach'.split()


def parse(text):
    # Preserve backslashes in Windows paths. Quoting groups spaces; no escapes or expansions.
    if any(c in text for c in '|;&><`\n\r') or '$(' in text:
        raise ValueError('Pipes, redirects and shell expressions are unsupported / Конструкции shell не поддерживаются')
    parts, current, quote, active = [], '', None, False
    for ch in text:
        if quote:
            if ch == quote:
                quote = None
            else:
                current += ch
        elif ch in ('"', "'"):
            quote, active = ch, True
        elif ch.isspace():
            if active:
                parts.append(current)
                current, active = '', False
        else:
            current += ch
            active = True
    if quote:
        raise ValueError('Unclosed quote / Незакрытая кавычка')
    if active:
        parts.append(current)
    return parts


@dataclass
class Result:
    output: str = ''
    action: str = ''
    confirmation: str = ''
    success: bool = True


class Engine:
    def __init__(self, cwd=None):
        self.cwd = Path(cwd or Path.home()).resolve()

    def path(self, value):
        p = Path(value).expanduser()
        return p if p.is_absolute() else self.cwd / p

    def read(self, value):
        p = self.path(value)
        with p.open('rb') as file:
            data = file.read(1024 * 1024 + 1)
        if len(data) > 1024 * 1024:
            raise ValueError('File exceeds 1 MiB / Файл больше 1 МиБ')
        return data.decode('utf-8-sig')

    def execute(self, text, confirmed=False):
        try:
            return self._execute(parse(text), confirmed)
        except (OSError, ValueError, TypeError, IndexError, psutil.Error) as exc:
            return Result(f'ERROR / ОШИБКА: {exc}', success=False)

    def _execute(self, parts, confirmed):
        if not parts:
            return Result()
        cmd, *a = parts
        if cmd not in COMMANDS:
            return Result(f'Unknown command / Неизвестная команда: {cmd}. help', success=False)
        def arity(low, high=None):
            if not low <= len(a) <= (low if high is None else high):
                raise ValueError(f'{cmd}: arguments / аргументы: {low}..{high if high is not None else low}')
        if cmd == 'help':
            return Result('COMMANDS / КОМАНДЫ\n' + '  '.join(COMMANDS) + '\n\nrun "C:\\path\\app.exe" [args] — launch / запуск\nopen <path> — open file/folder / открыть\nls [-a|-l|-la] [path]; mkdir [-p] <dir>; grep [-i] <text> <file>\nhead/tail [-n count] <file>; cp/mv <src> <dst>; rm <file>; kill <pid>\nNo Bash/WSL emulation. Package managers are reference only.\nНет эмуляции Bash/WSL. Пакетные менеджеры — справка.')
        if cmd in ('clear', 'history', 'breach'):
            arity(0, 1 if cmd == 'breach' else 0)
            return Result(action=cmd)
        if cmd == 'pwd':
            arity(0); return Result(str(self.cwd))
        if cmd == 'cd':
            arity(0, 1); p = self.path(a[0]) if a else Path.home()
            p = p.resolve(strict=True)
            if not p.is_dir(): raise ValueError('Not a directory / Не каталог')
            self.cwd = p; return Result(str(p))
        if cmd == 'ls':
            flags = [v for v in a if v.startswith('-')]
            if any(v not in ('-a','-l','-la','-al') for v in flags): raise ValueError('Unknown ls flag')
            names = [v for v in a if not v.startswith('-')]
            if len(names) > 1: raise ValueError('ls [path]')
            p = self.path(names[0]) if names else self.cwd
            items = sorted(p.iterdir(), key=lambda v: v.name.lower()) if p.is_dir() else [p]
            show_hidden = any('a' in f for f in flags)
            lines = []
            for v in items[:2000]:
                if not show_hidden and (v.name.startswith('.') or (os.name == 'nt' and getattr(v.stat(), 'st_file_attributes', 0) & 2)): continue
                lines.append((f'{v.stat().st_size:>12}  ' if any('l' in f for f in flags) else '') + v.name + ('/' if v.is_dir() else ''))
            return Result('\n'.join(lines))
        if cmd in ('cat','head','tail','grep','wc','sort','uniq'):
            insensitive = cmd == 'grep' and a and a[0] == '-i'
            if insensitive: a = a[1:]
            n = 10
            if cmd in ('head','tail') and len(a) == 3 and a[0] == '-n':
                n = int(a[1]); a = a[2:]
                if not 0 <= n <= 10000: raise ValueError('count: 0..10000')
            arity(2 if cmd == 'grep' else 1)
            value = self.read(a[-1]); lines = value.splitlines()
            if cmd == 'cat': return Result(value)
            if cmd == 'head': lines = lines[:n]
            if cmd == 'tail': lines = lines[-n:] if n else []
            if cmd == 'grep': lines = [v for v in lines if (a[0].casefold() in v.casefold() if insensitive else a[0] in v)]
            if cmd == 'wc': return Result(f'{len(lines)} lines / строк; {len(value.split())} words / слов; {len(value.encode())} bytes')
            if cmd == 'sort': lines = sorted(lines)
            if cmd == 'uniq': lines = [v for i,v in enumerate(lines) if i == 0 or v != lines[i-1]]
            return Result('\n'.join(lines))
        if cmd in ('mkdir','touch'):
            parents = cmd == 'mkdir' and a and a[0] == '-p'
            if parents: a = a[1:]
            arity(1)
            if a[0].startswith('-'): raise ValueError('Unsupported flag')
            p = self.path(a[0])
            if cmd == 'mkdir': p.mkdir(parents=bool(parents), exist_ok=bool(parents))
            else: p.touch(exist_ok=True)
            return Result(str(p))
        if cmd in ('cp','mv','rm','rmdir','kill','run','open'):
            arity(2 if cmd in ('cp','mv') else 1, 100 if cmd == 'run' else (2 if cmd in ('cp','mv') else 1))
            if a[0].startswith('-'): raise ValueError('Unsupported flag / Флаг не поддерживается')
            p = self.path(a[0]) if cmd not in ('kill','run') else None
            if cmd in ('rm','rmdir','kill','run','open') and not confirmed:
                detail = ''
                if cmd == 'kill':
                    proc = psutil.Process(int(a[0])); detail = f'\n{proc.name()} / {proc.username()}'
                if cmd == 'run':
                    target = Path(shutil.which(a[0]) or str(self.path(a[0]))).resolve(strict=True)
                    detail = f'\n{target}'
                if cmd == 'rm': detail = '\nPermanent deletion / Безвозвратное удаление файла'
                return Result(confirmation=f'{cmd}: {" ".join(a)}{detail}\nConfirm action / Подтвердите действие.')
            if cmd in ('cp','mv'):
                dest = self.path(a[1])
                if dest.is_dir(): dest = dest / p.name
                # No overwrites, including broken links.
                if dest.exists() or dest.is_symlink(): raise ValueError('Destination exists / Назначение уже существует')
                if p.is_symlink(): raise ValueError('Symlinks unsupported / Символические ссылки не поддерживаются')
                if not p.is_file(): raise ValueError('Only files / Только файлы')
                with p.open('rb') as src, dest.open('xb') as dst: shutil.copyfileobj(src, dst)
                if cmd == 'mv': p.unlink()
                return Result(str(dest))
            if cmd == 'rm':
                if p.is_dir() or p.is_symlink(): raise ValueError('Only regular files / Только обычные файлы')
                p.unlink()
            if cmd == 'rmdir': p.rmdir()
            if cmd == 'kill':
                pid = int(a[0]); proc = psutil.Process(pid)
                if pid in (0,1,4,os.getpid()) or proc.username() != psutil.Process().username(): raise ValueError('Protected process / Защищённый процесс')
                proc.terminate()
            if cmd == 'run':
                executable = shutil.which(a[0]) or str(self.path(a[0]))
                target = Path(executable).resolve(strict=True)
                if not target.is_file() or (os.name == 'nt' and target.suffix.lower() != '.exe'):
                    raise ValueError('Select an executable (.exe on Windows)')
                proc = subprocess.Popen([str(target), *a[1:]], cwd=self.cwd, shell=False, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return Result(f'PID {proc.pid}')
            if cmd == 'open':
                p = p.resolve(strict=True)
                if p.is_file() and p.suffix.lower() not in ('.txt','.md','.png','.jpg','.jpeg','.pdf','.json','.csv','.log'):
                    raise ValueError('Use run for programs / Для программ используйте run')
                if os.name == 'nt': os.startfile(str(p))
                else: subprocess.Popen(['open' if platform.system() == 'Darwin' else 'xdg-open', str(p)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return Result('OK')
        if cmd in ('stat','du','df'):
            arity(0 if cmd == 'df' else 1,1); p = self.path(a[0]) if a else self.cwd
            if cmd == 'df':
                v = shutil.disk_usage(p); return Result(f'Total {v.total:,}; Used {v.used:,}; Free {v.free:,} bytes')
            s = p.stat()
            if cmd == 'du' and p.is_dir(): raise ValueError('du supports files only / du пока только для файлов')
            return Result(f'{p}\n{s.st_size:,} bytes\n{datetime.fromtimestamp(s.st_mtime).isoformat()}')
        if cmd in ('basename','dirname','realpath','which'):
            arity(1)
            return Result(str({'basename':lambda:Path(a[0]).name,'dirname':lambda:Path(a[0]).parent,'realpath':lambda:self.path(a[0]).resolve(),'which':lambda:shutil.which(a[0]) or 'Not found / Не найдено'}[cmd]()))
        if cmd in ('echo','env','printenv'):
            if cmd == 'echo': return Result(' '.join(a))
            arity(0,1)
            return Result(os.environ.get(a[0], '') if a else '\n'.join(sorted(os.environ)))
        if cmd in ('date','whoami','hostname','uname','uptime','ps'):
            arity(0)
            if cmd == 'date': return Result(datetime.now().astimezone().isoformat())
            if cmd == 'whoami': return Result(getpass.getuser())
            if cmd == 'hostname': return Result(platform.node())
            if cmd == 'uname': return Result(platform.platform())
            if cmd == 'uptime': return Result(f'{(time.time()-psutil.boot_time())/3600:.2f} h')
            rows=[]
            for p in psutil.process_iter(['pid','name','memory_info'], ad_value=None):
                d=p.info; mem=d['memory_info']; rows.append(f"{d['pid']:>7} {(mem.rss // 1048576) if mem else 0:>7} MiB  {d['name']}")
            return Result('\n'.join(rows[:1000]))
        if cmd in ('explain','preview','translate'):
            arity(1,100)
            if a[0] not in COMMANDS: raise ValueError('Unknown command')
            if cmd == 'translate':
                mapping={'ls':'Get-ChildItem','pwd':'Get-Location','cd':'Set-Location','cat':'Get-Content','mkdir':'New-Item -ItemType Directory','ps':'Get-Process'}
                return Result('Approximate / Приблизительно (не выполняется): '+mapping.get(a[0],'No translation / Нет перевода'))
            return Result(f'{a[0]}: {" ".join(a[1:])}\n'+('Changes files/processes or launches an app / Изменяет файлы/процессы или запускает приложение' if a[0] in ('cp','mv','rm','mkdir','touch','kill','run','open') else 'Local information / Локальные данные'))
        return Result('Unsupported')
