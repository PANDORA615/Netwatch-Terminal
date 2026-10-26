<p align="center">
  <img src="docs/banner.svg" alt="NETWATCH // TERMINAL — Your workspace. Your Linux dialect." width="100%">
</p>

<p align="center">
  <b>LOCAL FIRST · CYBERPUNK HUD · LINUX SYNTAX PROFILES</b><br>
  Python 3.12+ &nbsp; / &nbsp; PySide6 &nbsp; / &nbsp; Windows 10–11 &amp; Linux
</p>

<p align="center">
  <a href="docs/INSTALL.md">Запуск</a> ·
  <a href="docs/SCREENSHOTS.md">Скриншоты</a> ·
  <a href="docs/FEATURES.md">Возможности</a> ·
  <a href="https://github.com/PANDORA615/Netwatch-Terminal/releases/latest">Скачать .exe</a>
</p>

Локальное desktop-приложение на Python 3.12+ и PySide6 в оригинальном cyberpunk-стиле. Целевая платформа — Windows 10/11 x64; интерфейс также можно запускать в Linux.

## Скачать для Windows

### [⬇ Скачать NETWATCH Terminal — Windows x64 (ZIP)](https://github.com/PANDORA615/Netwatch-Terminal/releases/latest/download/NetwatchTerminal-Windows-x64.zip)

**Python и вход в GitHub не нужны.** Скачайте ZIP → **Извлечь всё** → запустите `NetwatchTerminal.exe`. Сохраните рядом папку `_internal`. Это переносимая тестовая версия для Windows 10/11 x64.

[Страница релиза](https://github.com/PANDORA615/Netwatch-Terminal/releases/latest) · [Подробная установка](docs/INSTALL.md)

## Интерфейс

Лаймовые панели, тонкие технические рамки, статичные скан-линии и тёмный фиолетовый фон. Оформление создано для проекта по мотивам cyberpunk-терминалов; изображения ниже — снимки работающего приложения PySide6.

![Terminal — профиль Ubuntu, поле ввода и справка синтаксиса](docs/terminal-preview.png)

<table>
  <tr>
    <td width="50%"><img src="docs/dashboard-preview.png" alt="Dashboard: системная панель в новой HUD-теме"><br><b>SYS//PULSE</b> — экран системного обзора</td>
    <td width="50%"><img src="docs/arch-preview.png" alt="Terminal: выбран Arch Linux и показаны команды pacman"><br><b>ARCH PROFILE</b> — приглашение и подсказки pacman</td>
  </tr>
</table>

![Профили Linux и их пакетные менеджеры](docs/profiles.svg)

## Версия 0.2.0 — рабочие модули

- **Терминал:** реальные операции с файлами, текстом и процессами; `help` показывает список команд.
- **Запуск программ:** `run notepad.exe` или `run "C:\Program Files\App\app.exe"` с подтверждением. Аргументы передаются отдельно, без shell.
- **Обзор и система:** реальные CPU/RAM/диск, время обновления, процессы.
- **Сеть:** локальные интерфейсы, адреса и скорости RX/TX без сканирования.
- **Файлы:** дерево каталогов, выбор папки, открытие поддерживаемых файлов с подтверждением.
- **Программы:** сохранённое избранное, добавление и запуск выбранных приложений.
- **BreachLab:** оригинальная решаемая головоломка 5×5, буфер из 6 ходов, перезапуск и рекорд.
- **Настройки:** русский/английский язык, сохранение Linux-профиля, полного экрана, истории и избранного.
- **Полный экран:** при первом запуске по умолчанию, поверх панели задач. `F11` переключает, `Esc` возвращает окно. Кнопка «Выход» закрывает приложение.
- **Автозапуск Windows:** по желанию в настройках или установщике, по умолчанию выключен. Работает при входе текущего пользователя, отключается в настройках.

### Установка в Windows

**[⬇ Скачать установщик .exe](https://github.com/PANDORA615/Netwatch-Terminal/releases/latest/download/NetwatchTerminal-Setup-x64.exe)**

Запустите установщик → выберите папку → при желании отметьте ярлык и автозапуск → установите. Python и права администратора не нужны. Удаление — через «Установленные приложения» Windows. Автозапуск можно менять после установки.

Альтернатива: [переносимый ZIP](https://github.com/PANDORA615/Netwatch-Terminal/releases/latest/download/NetwatchTerminal-Windows-x64.zip) → «Извлечь всё» → `NetwatchTerminal.exe`. Сохраните `_internal` рядом. На Android/iPhone Windows `.exe` не запускается.

**[Полная установка и решение ошибок →](docs/INSTALL.md)** · **[Команды и ограничения →](docs/FEATURES.md)**

### Границы совместимости

Это Windows-приложение с собственным Linux-подобным движком, а не Linux/WSL или полный Bash. Пайпы, перенаправления, подстановки, sudo, пакетные менеджеры и команды, которым нужно ядро Linux, не исполняются. Linux-профили меняют справку и приглашение, а не ОС.

`rm` удаляет один файл безвозвратно только после подтверждения; рекурсивного удаления и перезаписи нет. `cp`/`mv` работают с отдельными файлами и отклоняют конфликты. `kill` требует подтверждения и ограничен процессами текущего пользователя. `run` запускает выбранный исполняемый файл после подтверждения; в Windows поддерживаются `.exe`, не `.bat`/`.cmd`. Чтение текстовых файлов ограничено 1 МиБ, вывод — 100 тысячами символов. Большие операции выполняются вне потока интерфейса.

История выключена по умолчанию; при включении может содержать личные пути. Команды `run`, `env`, `printenv`, `cat`, `echo` и строки с признаками секретов в историю не записываются. Это фильтр, а не гарантия распознавания всех секретов; историю можно отключить и очистить.

### Запуск из исходников в Windows

Установите [Python 3.12 x64](https://www.python.org/downloads/windows/), включая Python Launcher и пункт **Add python.exe to PATH**. Скачайте репозиторий через **Code → Download ZIP**, распакуйте его и откройте PowerShell в папке, содержащей `pyproject.toml` (правый клик в пустом месте папки → **Открыть в Терминале**).

Выполните команды по очереди:

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m netwatch_terminal
```

Для следующих запусков откройте PowerShell в той же папке и выполните только последнюю команду. Активация окружения и изменение политики PowerShell не требуются. Интернет нужен для первой установки зависимостей.

## Проверка вручную

1. Введите `help`, затем `pwd`, `ls`, `mkdir "test folder"`, `cd "test folder"`, `touch demo.txt`, `ls -la`.
2. В Windows введите `run notepad.exe`: отмените первое подтверждение, затем подтвердите повторный запуск.
3. `rm demo.txt`: проверьте предупреждение и отмену; затем при необходимости подтвердите удаление тестового файла.
4. Переключите профили Linux, проверьте реальные метрики на Обзоре, адреса в Сети и дерево Файлов.
5. Добавьте `.exe` в Программы, запустите его; в BreachLab соберите целевую последовательность.
6. В Настройках поменяйте язык, профиль, историю и режим экрана; перезапустите приложение и проверьте сохранение.
7. `F11` — полный экран, `Esc` — окно, `Ctrl+1`…`Ctrl+8` — разделы, `Ctrl+L` — ввод, `Tab` — дополнение имени команды, `↑`/`↓` — включённая история.
8. В Windows включите и выключите автозапуск. Для полной проверки включите его, выйдите из учётной записи и войдите снова; затем отключите и повторите. Установщик также предлагает необязательный автозапуск.

## Тесты и снимок окна

Для разработки сначала установите дополнительные зависимости:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m netwatch_terminal --screenshot docs/terminal-preview.png
.\.venv\Scripts\python.exe scripts/render_previews.py
```

CI запускает pytest и рендер окна на Linux и Windows, затем собирает Windows-приложение. В разделе [Actions](https://github.com/PANDORA615/Netwatch-Terminal/actions) после успешного запуска скачайте артефакт `NetwatchTerminal-Windows-x64`, распакуйте всю папку и запустите `NetwatchTerminal.exe`. Это тестовая сборка; проверка на чистой Windows 10/11 отдельно ещё требуется.

Сборка вручную в Windows:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --windowed --onedir --name NetwatchTerminal src/netwatch_terminal/__main__.py --paths src
```

## Структура

- `core/engine.py` — разбор, команды, файловые операции и запуск программ.
- `core/settings.py` — настройки пользователя и Windows HKCU Run.
- `core/breach.py` — решаемая модель BreachLab.
- `ui/` — русско/англоязычные экраны и фоновые задачи Qt.
- `installer/netwatch.iss` — установщик Inno Setup с удалением и необязательным автозапуском.
- `tests/` — команды на временных файлах, запреты, подтверждения, настройки, игра и UI.
- `.github/workflows/ci.yml` — проверки Windows/Linux, smoke-тест упакованного `.exe`, установщик и публикация релизов по тегам `v*`.

Неофициальный фанатский проект. Не связан с CD PROJEKT RED; игровые логотипы, музыка и ассеты не используются. Перед коммерческим выпуском необходимо проверить название и товарные знаки. Код — MIT; сторонние зависимости распространяются по собственным лицензиям.
