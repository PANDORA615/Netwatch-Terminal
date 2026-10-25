# NETWATCH//TERMINAL

Локальное desktop-приложение на Python 3.12+ и PySide6 в оригинальном cyberpunk-стиле. Целевая платформа — Windows 10/11 x64; интерфейс также можно запускать в Linux.

![Запущенный интерфейс PySide6](docs/terminal-preview.png)

## Текущая версия: этапы 0–1

Готовы src-layout, точка входа, тёмная тема, восемь экранов навигации, клавиатурное управление и заглушки Dashboard/Terminal. Интерфейс по умолчанию английский.

В Terminal доступны профили **Ubuntu, Debian, Fedora, Arch Linux, Kali Linux, openSUSE, Alpine**. Выбор меняет приглашение, справочную оболочку и подсказки пакетного менеджера: `apt`, `dnf`, `pacman`, `zypper`, `apk`. Общие команды `pwd`, `ls`, `cd`, `cat`, `mkdir` имеют общий базовый синтаксис. Shell и пакетный менеджер — разные вещи; профиль не устанавливает дистрибутив и не включает Bash/WSL. Оболочка указана как типичный профиль и может отличаться в конкретной установке. Fedora check-update проверяет обновления, Arch -Syu обновляет систему. Наличие sudo зависит от установки Linux.

Поле ввода принимает текст и показывает уведомление о предпросмотре. **Команды пока не выполняются**, ввод не записывается в историю. Нет реальных системных метрик, файловых операций, сетевых запросов и BreachLab; соответствующие экраны помечены как запланированные. Настройки и выбранный профиль пока действуют только в текущем сеансе; анимации отключены.

## Запуск в Windows (PowerShell)

```powershell
git clone https://github.com/PANDORA615/Netwatch-Terminal.git
cd Netwatch-Terminal
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m netwatch_terminal
```

В Linux:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m netwatch_terminal
```

Нужен графический сеанс. Для проверки без дисплея используйте `QT_QPA_PLATFORM=offscreen`.

## Проверка вручную

1. Откройте Terminal и переключите все профили: приглашение и справка должны обновиться.
2. Введите текст и нажмите Enter или Preview: появится уведомление, ввод очистится, действия не выполнятся.
3. Переключите все разделы слева; Dashboard показывает `unavailable`, а не вымышленные показатели.
4. Проверьте окно размером 1000×650, выделение/копирование вывода и прокрутку справки.
5. `Ctrl+1`…`Ctrl+8` переключают разделы, `Ctrl+L` открывает Terminal и фокусирует ввод; Tab перемещает фокус.

## Тесты и снимок окна

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m netwatch_terminal --screenshot docs/terminal-preview.png
```

CI запускает pytest и рендер окна на Linux и Windows, затем собирает Windows-приложение. В разделе [Actions](https://github.com/PANDORA615/Netwatch-Terminal/actions) после успешного запуска скачайте артефакт `NetwatchTerminal-Windows-x64`, распакуйте всю папку и запустите `NetwatchTerminal.exe`. Это тестовая сборка; проверка на чистой Windows 10/11 отдельно ещё требуется.

Сборка вручную в Windows:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --windowed --onedir --name NetwatchTerminal src/netwatch_terminal/__main__.py --paths src
```

## Структура и следующий этап

- `src/netwatch_terminal/app.py` — создание QApplication и запуск.
- `src/netwatch_terminal/core/distributions.py` — профили и справочные команды без зависимости от Qt.
- `src/netwatch_terminal/ui/` — окно, навигация, тема и заглушки.
- `tests/` — импорт, навигация, профили, размеры и безопасный предпросмотр ввода.
- `.github/workflows/ci.yml` — проверки и Windows-сборка.

Следующий этап ТЗ: собственные CommandParser/Registry/Executor и безопасные `help`, `clear`, `pwd`, `ls`, `cd`, `cat`, `mkdir`, затем история. Полный Bash-синтаксис и произвольный shell-код не планируются. Мониторинг — этап 3, остальные модули — последующие этапы.

Неофициальный фанатский проект. Не связан с CD PROJEKT RED; игровые логотипы, музыка и ассеты не используются. Перед коммерческим выпуском необходимо проверить название и товарные знаки. Код проекта — MIT; сторонние зависимости распространяются по собственным лицензиям (включая Qt/PySide6).
