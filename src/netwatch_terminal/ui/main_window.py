"""Functional desktop views. Blocking commands and metrics run outside the UI thread."""
import json
import os
from pathlib import Path
import platform
import time
import psutil
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QEvent
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPlainTextEdit, QPushButton, QScrollArea,
    QStackedWidget, QVBoxLayout, QWidget, QMessageBox, QFileDialog, QListWidget,
    QTreeView, QGridLayout, QFileSystemModel)
from ..core.distributions import DISTRIBUTIONS
from ..core.engine import Engine, COMMANDS, Result
from ..core.settings import Settings, startup_enabled, set_startup
from ..core.breach import Puzzle
from .hud import HudCanvas

MODULES = ('DASHBOARD','TERMINAL','SYSTEM','NETWORK','FILES','LAUNCHER','BREACHLAB','SETTINGS')
RUSSIAN = ('ОБЗОР','ТЕРМИНАЛ','СИСТЕМА','СЕТЬ','ФАЙЛЫ','ПРОГРАММЫ','BREACHLAB','НАСТРОЙКИ')


def label(text, kind=None):
    w = QLabel(text); w.setWordWrap(True)
    if kind: w.setObjectName(kind)
    w.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return w


def panel():
    w=QFrame(); w.setObjectName('panel'); box=QVBoxLayout(w); box.setContentsMargins(18,18,18,18)
    return w,box


class Worker(QThread):
    done = Signal(object)
    def __init__(self, task):
        super().__init__(); self.task=task
    def run(self):
        try: self.done.emit(self.task())
        except Exception as exc: self.done.emit(Result(str(exc), success=False))


class MainWindow(QMainWindow):
    def __init__(self, settings=None, monitoring=True):
        super().__init__()
        self.settings=settings or Settings(); self.engine=Engine()
        self.texts=[]; self.workers=[]; self.history=[]; self.history_index=0; self.busy=False
        if self.settings.data.get('history'):
            self.history=list(self.settings.data.get('commands',[]))[-200:]
        self.history_index=len(self.history)
        self.setWindowTitle('NETWATCH // TERMINAL'); self.setMinimumSize(1000,650); self.resize(1440,900)
        root=HudCanvas(); self.setCentralWidget(root); shell=QHBoxLayout(root); shell.setContentsMargins(0,0,0,0)
        sidebar=QFrame(); sidebar.setObjectName('sidebar'); sidebar.setFixedWidth(218)
        nav=QVBoxLayout(sidebar); nav.setContentsMargins(16,20,16,15); nav.setSpacing(7)
        nav.addWidget(label('NETWATCH','brand')); nav.addWidget(label('▰▰▰▰▰▰▰▰▰▰','accent'))
        nav.addWidget(self.lbl('LOCAL OPERATIONS','ЛОКАЛЬНАЯ СЕССИЯ','muted'))
        self.group=QButtonGroup(self); self.buttons=[]
        for i,name in enumerate(MODULES):
            b=QPushButton(); b.setCheckable(True); self.group.addButton(b,i); self.buttons.append(b); nav.addWidget(b)
        nav.addStretch(); nav.addWidget(label('v0.2.1 / LOCAL','accent'))
        exit_button=self.button('Exit','Выход',self.close); nav.addWidget(exit_button)
        shell.addWidget(sidebar)
        content=QVBoxLayout(); content.setContentsMargins(25,18,25,12); content.setSpacing(8); shell.addLayout(content,1)
        top=QHBoxLayout(); top.addWidget(self.lbl('PERSONAL CONSOLE / NW–02','ЛИЧНАЯ КОНСОЛЬ / NW–02','muted')); top.addStretch()
        top.addWidget(self.button('Fullscreen [F11]','На весь экран [F11]',self.toggle_fullscreen)); content.addLayout(top)
        self.pages=QStackedWidget(); content.addWidget(self.pages,1)
        self.pages.addWidget(self.dashboard_page())
        self.pages.addWidget(self.terminal_page())
        self.pages.addWidget(self.info_page('SYSTEM','СИСТЕМА','system_output'))
        self.pages.addWidget(self.info_page('NETWORK','СЕТЬ','network_output'))
        self.pages.addWidget(self.files_page())
        self.pages.addWidget(self.launcher_page())
        self.pages.addWidget(self.breach_page())
        self.pages.addWidget(self.settings_page())
        self.group.idClicked.connect(self.navigate)
        for i in range(8):
            QShortcut(QKeySequence(f'Ctrl+{i+1}'),self).activated.connect(lambda n=i:self.navigate(n))
        QShortcut(QKeySequence('Ctrl+L'),self).activated.connect(self.focus_input)
        QShortcut(QKeySequence('F11'),self).activated.connect(self.toggle_fullscreen)
        QShortcut(QKeySequence('Escape'),self).activated.connect(self.leave_fullscreen)
        self.apply_language(); self.navigate(1)
        self.command_input.setFocus()
        self.metrics_timer=QTimer(self); self.metrics_timer.timeout.connect(self.refresh_metrics)
        if monitoring:
            self.metrics_timer.start(2000); self.refresh_metrics()

    def tr2(self,en,ru): return ru if self.settings.data.get('language')=='ru' else en
    def lbl(self,en,ru,kind=None):
        w=label(self.tr2(en,ru),kind); self.texts.append((w,en,ru)); return w
    def button(self,en,ru,callback):
        b=QPushButton(self.tr2(en,ru)); self.texts.append((b,en,ru)); b.clicked.connect(callback); return b
    def page(self,en,ru):
        w=QWidget(); box=QVBoxLayout(w); box.setContentsMargins(0,0,0,0); box.setSpacing(6)
        box.addWidget(self.lbl(en,ru,'title')); return w,box
    def start(self,task,callback):
        worker=Worker(task); self.workers.append(worker)
        worker.done.connect(callback)
        def cleanup():
            if worker in self.workers: self.workers.remove(worker)
            if getattr(self,'closing',False) and not self.workers: QTimer.singleShot(0,self.close)
        worker.finished.connect(cleanup)
        worker.start()
    def save(self):
        try: self.settings.save()
        except OSError as exc: self.statusBar().showMessage(str(exc))
    def apply_language(self):
        for w,en,ru in self.texts: w.setText(self.tr2(en,ru))
        for i,b in enumerate(self.buttons): b.setText(f'{i+1:02}  '+self.tr2(MODULES[i],RUSSIAN[i]))
        self.command_input.setPlaceholderText(self.tr2('Command… help for available commands','Команда… help — список команд'))
        self.statusBar().showMessage(self.tr2('F11 Fullscreen • Esc Window • Tab Complete • ↑↓ History','F11 Полный экран • Esc Окно • Tab Дополнение • ↑↓ История'))
    def navigate(self,index): self.pages.setCurrentIndex(index); self.buttons[index].setChecked(True)
    def focus_input(self): self.navigate(1); self.command_input.setFocus()
    def toggle_fullscreen(self):
        if self.isFullScreen(): self.showNormal()
        else: self.showFullScreen()
        self.settings.data['fullscreen']=self.isFullScreen(); self.fullscreen_check.setChecked(self.isFullScreen()); self.save()
    def leave_fullscreen(self):
        if self.isFullScreen(): self.toggle_fullscreen()

    def terminal_page(self):
        w,box=self.page('NETRUNNER//SHELL','NETRUNNER//ТЕРМИНАЛ')
        row=QHBoxLayout(); self.distribution=QComboBox(); self.distribution.addItems([d.name for d in DISTRIBUTIONS])
        self.distribution.setCurrentIndex(max(0,min(6,int(self.settings.data.get('profile',0)))))
        row.addWidget(self.lbl('LINUX PROFILE','ПРОФИЛЬ LINUX','muted')); row.addWidget(self.distribution)
        self.profile_info=label('','accent'); row.addWidget(self.profile_info); box.addLayout(row)
        middle=QHBoxLayout(); self.output=QPlainTextEdit(); self.output.setReadOnly(True); self.output.setMinimumHeight(170)
        self.output.document().setMaximumBlockCount(3000); terminal, terminal_box=panel(); terminal_box.setContentsMargins(0,0,0,0); terminal_box.addWidget(self.lbl('COMMAND INTERFACE / LOCAL','КОМАНДНЫЙ ИНТЕРФЕЙС / LOCAL','section')); terminal_box.addWidget(self.output); middle.addWidget(terminal,3)
        self.syntax=label(''); self.syntax.setAlignment(Qt.AlignmentFlag.AlignTop); reference=QScrollArea(); reference.setWidgetResizable(True); reference.setWidget(self.syntax); reference.setMaximumWidth(340)
        middle.addWidget(reference,1); box.addLayout(middle,1)
        self.prompt=label('','accent'); box.addWidget(self.prompt)
        row=QHBoxLayout(); self.command_input=QLineEdit(); self.command_input.setMaxLength(4096); self.command_input.installEventFilter(self)
        self.command_input.returnPressed.connect(self.submit); row.addWidget(self.command_input,1)
        self.submit_button=self.button('Execute ↵','Выполнить ↵',self.submit); row.addWidget(self.submit_button); box.addLayout(row)
        box.addWidget(self.lbl('run <program> [args] • help • Package managers are reference only','run <программа> [аргументы] • help • Пакетные менеджеры — только справка','muted'))
        self.distribution.currentIndexChanged.connect(self.update_profile); self.update_profile(self.distribution.currentIndex())
        self.output.setPlainText('NETWATCH 0.2.1\n\n'+self.tr2('Local command engine ready. Type help.','Локальный терминал готов. Введите help.'))
        return w
    def update_profile(self,index):
        d=DISTRIBUTIONS[index]; self.settings.data['profile']=index
        self.profile_info.setText(f'{d.shell.upper()} / {d.manager.upper()}')
        self.syntax.setText(self.tr2('LINUX REFERENCE (not executed)\n\n','СПРАВКА LINUX (не выполняется)\n\n')+f'{d.refresh}\n\n{d.install}\n\n{d.search}\n\n'+self.tr2('Common commands:','Общие команды:')+'\npwd\nls -la\ncd "path"\ncat "file"\nrun notepad.exe\n\nhelp')
        self.update_prompt()
        if hasattr(self,'language_combo'): self.save()
    def update_prompt(self):
        d=DISTRIBUTIONS[self.distribution.currentIndex()]; self.prompt.setText(f'operator@{d.slug}:{self.engine.cwd}$')
    def submit(self):
        if self.busy: return
        text=self.command_input.text().strip()
        if not text: return
        self.command_input.clear()
        # Persistence is opt-in; omit launches and environment/file reads to limit sensitive history.
        first=text.split()[0]
        if self.settings.data.get('history') and first not in ('run','env','printenv','cat','echo') and not any(s in text.lower() for s in ('password','token','secret')):
            self.history=(self.history+[text])[-200:]; self.settings.data['commands']=self.history; self.save()
        self.history_index=len(self.history)
        self.busy=True; self.command_input.setEnabled(False); self.submit_button.setEnabled(False)
        def done(result):
            if result.confirmation:
                accepted=self.confirm(result.confirmation)
                if accepted:
                    self.start(lambda:self.engine.execute(text,True),done); return
                result=Result(self.tr2('Cancelled','Отменено'))
            if result.action=='clear': self.output.clear()
            elif result.action=='breach': self.navigate(6)
            elif result.action=='history': self.output.appendPlainText('\n'.join(self.history) or self.tr2('History disabled or empty','История отключена или пуста'))
            else: self.output.appendPlainText(result.output[:100000])
            self.update_prompt(); self.busy=False; self.command_input.setEnabled(True); self.submit_button.setEnabled(True); self.command_input.setFocus()
        self.start(lambda:self.engine.execute(text),done)
    def confirm(self,text):
        return QMessageBox.question(self,self.tr2('Confirm action','Подтверждение'),text,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes
    def eventFilter(self,obj,event):
        if obj is self.command_input and event.type()==QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Up,Qt.Key.Key_Down):
                self.history_index=max(0,min(len(self.history),self.history_index+(-1 if event.key()==Qt.Key.Key_Up else 1)))
                self.command_input.setText(self.history[self.history_index] if self.history_index<len(self.history) else ''); return True
            if event.key()==Qt.Key.Key_Tab:
                prefix=self.command_input.text(); matches=[c for c in COMMANDS if c.startswith(prefix)]
                if len(matches)==1:self.command_input.setText(matches[0]+' ')
                elif matches:self.output.appendPlainText('  '.join(matches))
                return True
        return super().eventFilter(obj,event)

    def dashboard_page(self):
        w,box=self.page('SYS//PULSE','SYS//ОБЗОР'); self.metric_labels=[]; row=QHBoxLayout()
        for en,ru in [('CPU','ПРОЦЕССОР'),('RAM','ПАМЯТЬ'),('DISK','ДИСК')]:
            f,b=panel(); b.addWidget(self.lbl(en,ru,'accent')); value=label('—','title'); b.addWidget(value); self.metric_labels.append(value); row.addWidget(f)
        box.addLayout(row); self.metric_status=label('','muted'); box.addWidget(self.metric_status); box.addStretch(); return w
    def info_page(self,en,ru,attr):
        w,box=self.page(en,ru); output=QPlainTextEdit(); output.setReadOnly(True); setattr(self,attr,output); box.addWidget(output); return w
    def refresh_metrics(self):
        if getattr(self,'metrics_busy',False): return
        self.metrics_busy=True
        def sample():
            cpu=psutil.cpu_percent(interval=0.1); mem=psutil.virtual_memory(); disk=psutil.disk_usage(Path.home().anchor)
            addresses=psutil.net_if_addrs(); counters=psutil.net_io_counters()
            return cpu,mem,disk,addresses,counters,time.monotonic(),Engine().execute('ps').output
        def done(result):
            self.metrics_busy=False
            if isinstance(result,Result):
                self.metric_status.setText('Unavailable / Недоступно: '+result.output); return
            cpu,mem,disk,addresses,counters,now,processes=result
            for value,text in zip(self.metric_labels,[f'{cpu:.1f}%',f'{mem.used/2**30:.1f}/{mem.total/2**30:.1f} GiB',f'{disk.free/2**30:.1f} GiB']):value.setText(text)
            self.metric_status.setText(self.tr2('Disk free • Updated: ','Свободно на диске • Обновлено: ')+time.strftime('%H:%M:%S'))
            self.system_output.setPlainText(platform.platform()+'\n'+platform.node()+f'\nCPU: {psutil.cpu_count()}\nRAM: {mem.total:,} bytes\nUptime: {(time.time()-psutil.boot_time())/3600:.2f} h\n\nPID / RAM / PROCESS\n'+processes)
            lines=[]
            if counters:
                if hasattr(self,'last_net'):
                    old,stamp=self.last_net; elapsed=max(.001,now-stamp)
                    lines.append(f'RX {(counters.bytes_recv-old.bytes_recv)/elapsed/1024:.1f} KiB/s  TX {(counters.bytes_sent-old.bytes_sent)/elapsed/1024:.1f} KiB/s')
                self.last_net=counters,now
                lines.append(f'RX total: {counters.bytes_recv:,} / TX total: {counters.bytes_sent:,} bytes')
            for name,entries in addresses.items():
                lines.append('\n'+name); lines.extend('  '+e.address for e in entries)
            self.network_output.setPlainText('\n'.join(lines))
        self.start(sample,done)

    def files_page(self):
        w,box=self.page('DATA//VAULT','DATA//ФАЙЛЫ')
        box.addWidget(self.button('Choose folder','Выбрать папку',self.choose_folder))
        self.file_model=QFileSystemModel(self); self.file_model.setRootPath(str(Path.home()))
        self.file_tree=QTreeView(); self.file_tree.setModel(self.file_model); self.file_tree.setRootIndex(self.file_model.index(str(Path.home()))); self.file_tree.setColumnWidth(0,350)
        self.file_tree.doubleClicked.connect(self.open_file); box.addWidget(self.file_tree); return w
    def choose_folder(self):
        path=QFileDialog.getExistingDirectory(self,self.tr2('Choose folder','Выберите папку'),str(self.engine.cwd))
        if path:self.file_tree.setRootIndex(self.file_model.index(path))
    def open_file(self,index):
        path=self.file_model.filePath(index)
        if Path(path).is_file(): self.command_input.setText('open "'+path+'"'); self.focus_input(); self.submit()
    def launcher_page(self):
        w,box=self.page('QUICK//JACK','QUICK//ПРОГРАММЫ'); self.favorites=QListWidget(); self.favorites.addItems(self.settings.data.get('favorites',[])); box.addWidget(self.favorites)
        box.addWidget(self.button('Add program','Добавить программу',self.add_program))
        box.addWidget(self.button('Launch selected','Запустить выбранную',self.launch_selected))
        box.addWidget(self.button('Remove from favorites','Убрать из избранного',self.remove_program)); return w
    def add_program(self):
        path,_=QFileDialog.getOpenFileName(self,self.tr2('Select executable','Выберите программу'),'', 'Programs (*.exe)' if os.name=='nt' else 'All files (*)')
        if path and path not in self.settings.data.get('favorites',[]):
            self.favorites.addItem(path); self.settings.data['favorites']=[self.favorites.item(i).text() for i in range(self.favorites.count())]; self.save()
    def launch_selected(self):
        if self.favorites.currentItem(): self.command_input.setText('run "'+self.favorites.currentItem().text()+'"'); self.focus_input(); self.submit()
    def remove_program(self):
        row=self.favorites.currentRow()
        if row>=0:self.favorites.takeItem(row); self.settings.data['favorites']=[self.favorites.item(i).text() for i in range(self.favorites.count())]; self.save()

    def breach_page(self):
        w,box=self.page('BREACH//LAB','BREACH//ЛАБОРАТОРИЯ'); self.game_status=label(''); box.addWidget(self.game_status)
        box.addWidget(self.lbl('Start in the top row, then alternate column / row. Match the sequence in 6 moves.','Начните с верхнего ряда, затем чередуйте столбец / ряд. Соберите последовательность за 6 ходов.','muted'))
        grid=QGridLayout(); self.cells=[]
        for r in range(5):
            for c in range(5):
                b=QPushButton(); b.clicked.connect(lambda checked=False,r=r,c=c:self.game_move(r,c)); grid.addWidget(b,r,c); self.cells.append(b)
        box.addLayout(grid); box.addWidget(self.button('New puzzle','Новая игра',self.new_game)); box.addWidget(self.button('Restart','Начать заново',self.restart_game)); self.new_game(); return w
    def new_game(self):self.game=Puzzle(); self.render_game()
    def restart_game(self):self.game.moves=[]; self.render_game()
    def game_move(self,r,c):
        self.game.choose(r,c)
        if self.game.won:
            best=min(int(self.settings.data.get('best',7)),len(self.game.moves)); self.settings.data['best']=best; self.save()
        self.render_game()
    def render_game(self):
        g=self.game; status=self.tr2('WIN','ПОБЕДА') if g.won else (self.tr2('BUFFER FULL','БУФЕР ЗАПОЛНЕН') if g.finished else self.tr2('CHOOSE A CELL','ВЫБЕРИТЕ ЯЧЕЙКУ'))
        self.game_status.setText(f'{status}\n{self.tr2("TARGET","ЦЕЛЬ")}: {" ".join(g.target)}   {self.tr2("BUFFER","БУФЕР")}: {" ".join(g.buffer)} ({len(g.moves)}/6)   {self.tr2("BEST","РЕКОРД")}: {self.settings.data.get("best","—")}')
        for i,b in enumerate(self.cells):
            r,c=divmod(i,5); b.setText(g.grid[r][c]+(' ✓' if (r,c) in g.moves else '')); b.setEnabled(g.allowed(r,c))

    def settings_page(self):
        w,box=self.page('SETTINGS','НАСТРОЙКИ'); self.language_combo=QComboBox(); self.language_combo.addItems(['Русский','English']); self.language_combo.setCurrentIndex(0 if self.settings.data.get('language')=='ru' else 1)
        box.addWidget(self.lbl('Language','Язык')); box.addWidget(self.language_combo)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.fullscreen_check=QCheckBox(); self.texts.append((self.fullscreen_check,'Start fullscreen (F11 / Esc)','Запускать на весь экран (F11 / Esc)')); self.fullscreen_check.setChecked(bool(self.settings.data.get('fullscreen')))
        self.fullscreen_check.toggled.connect(lambda v:self.preference('fullscreen',v)); box.addWidget(self.fullscreen_check)
        self.history_check=QCheckBox(); self.texts.append((self.history_check,'Save command history (paths may be private)','Сохранять историю команд (пути могут быть личными)')); self.history_check.setChecked(bool(self.settings.data.get('history')))
        self.history_check.toggled.connect(self.change_history); box.addWidget(self.history_check)
        box.addWidget(self.button('Clear history','Очистить историю',self.clear_history))
        self.startup_check=QCheckBox(); self.texts.append((self.startup_check,'Start with Windows (current user)','Запускать при входе в Windows (текущий пользователь)')); self.startup_check.setChecked(startup_enabled()); self.startup_check.setEnabled(os.name=='nt'); self.startup_check.toggled.connect(self.change_startup); box.addWidget(self.startup_check)
        box.addWidget(self.lbl('No animations. Fullscreen covers the taskbar; Esc returns to window. Autostart is optional and can be disabled here.','Анимации отключены. Полный экран закрывает панель задач; Esc возвращает окно. Автозапуск включается только по желанию.','muted')); box.addStretch(); return w
    def preference(self,key,value):self.settings.data[key]=value; self.save()
    def change_language(self,index):
        self.preference('language','ru' if index==0 else 'en'); self.apply_language(); self.update_profile(self.distribution.currentIndex()); self.render_game()
    def change_history(self,value):
        self.preference('history',value)
        if not value:self.clear_history()
    def clear_history(self):
        self.history=[]; self.history_index=0; self.settings.data.pop('commands',None); self.save()
    def change_startup(self,value):
        try:set_startup(value)
        except OSError as exc:
            self.startup_check.blockSignals(True); self.startup_check.setChecked(startup_enabled()); self.startup_check.blockSignals(False)
            QMessageBox.warning(self,'Windows',str(exc))
    def closeEvent(self,event):
        if any(w.isRunning() for w in self.workers):
            self.metrics_timer.stop(); self.closing=True
            self.statusBar().showMessage(self.tr2('Please wait for the operation to finish','Дождитесь завершения операции')); event.ignore(); return
        self.metrics_timer.stop(); event.accept()
