"""Stage 1 views. No shell, file operations, or simulated system metrics."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPlainTextEdit, QPushButton, QScrollArea,
    QStackedWidget, QVBoxLayout, QWidget,
)

from ..core.distributions import DISTRIBUTIONS

MODULES = ("DASHBOARD", "TERMINAL", "SYSTEM", "NETWORK", "FILES", "LAUNCHER", "BREACHLAB", "SETTINGS")


def label(text, kind=None):
    item = QLabel(text)
    if kind:
        item.setObjectName(kind)
    item.setWordWrap(True)
    item.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return item


def panel():
    frame = QFrame()
    frame.setObjectName("panel")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)
    return frame, layout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NETWATCH // TERMINAL — Interface Preview")
        self.setMinimumSize(1000, 650)
        self.resize(1360, 850)
        root = QWidget()
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(218)
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(18, 28, 18, 22)
        nav.setSpacing(9)
        nav.addWidget(label("NETWATCH", "brand"))
        nav.addWidget(label("// LOCAL OPERATIONS", "muted"))
        nav.addSpacing(30)
        nav.addWidget(label("WORKSPACE", "muted"))
        self.group = QButtonGroup(self)
        self.buttons = []
        for index, name in enumerate(MODULES):
            button = QPushButton(f"{index + 1:02}   {name}")
            button.setCheckable(True)
            button.setAccessibleName(name)
            self.group.addButton(button, index)
            self.buttons.append(button)
            nav.addWidget(button)
        nav.addStretch()
        nav.addWidget(label("●  LOCAL SESSION", "accent"))
        nav.addWidget(label("v0.1.0 / UI PREVIEW\nNo commands executed", "muted"))
        shell.addWidget(sidebar)
        content = QVBoxLayout()
        content.setContentsMargins(30, 22, 30, 12)
        content.setSpacing(18)
        shell.addLayout(content, 1)
        top = QHBoxLayout()
        workspace = label("PERSONAL CONSOLE  /  WORKSPACE 01", "muted")
        workspace.setWordWrap(False)
        top.addWidget(workspace)
        top.addStretch()
        offline = label("●  OFFLINE BY DESIGN", "accent")
        offline.setWordWrap(False)
        top.addWidget(offline)
        content.addLayout(top)
        self.pages = QStackedWidget()
        self.pages.addWidget(self.dashboard_page())
        self.pages.addWidget(self.terminal_page())
        descriptions = {
            "SYSTEM": "System details and process controls are planned for a later stage.",
            "NETWORK": "Local interfaces and traffic metrics are planned for stage 5.",
            "FILES": "Folder browsing and file tools are planned for a later stage.",
            "LAUNCHER": "Favorite applications and folders are planned for stage 5.",
            "BREACHLAB": "The original offline puzzle is planned for stage 6.",
        }
        for name in MODULES[2:7]:
            self.pages.addWidget(self.placeholder_page(name, descriptions[name]))
        self.pages.addWidget(self.settings_page())
        content.addWidget(self.pages, 1)
        content.addWidget(label("NETWATCH // TERMINAL     /     ORIGINAL INTERFACE     /     STAGE 01", "muted"))
        self.group.idClicked.connect(self.navigate)
        self.statusBar().showMessage("INTERFACE PREVIEW  •  Ctrl+1 Dashboard  /  Ctrl+2 Terminal  /  Ctrl+L Input")
        for index in range(len(MODULES)):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{index + 1}"), self)
            shortcut.activated.connect(lambda i=index: self.navigate(i))
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.focus_input)
        self.navigate(1)
        self.command_input.setFocus()

    def heading(self, layout, eyebrow, title, description):
        layout.addWidget(label(eyebrow, "accent"))
        layout.addWidget(label(title, "title"))
        layout.addWidget(label(description, "muted"))

    def terminal_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(15)
        self.heading(layout, "01 / INTERACTIVE WORKSPACE", "NETRUNNER//SHELL", "Choose your Linux profile. Explore its syntax before the command engine arrives.")
        toolbar = QHBoxLayout()
        toolbar.addWidget(label("LINUX PROFILE", "muted"))
        self.distribution = QComboBox()
        self.distribution.setAccessibleName("Linux distribution profile")
        self.distribution.addItems([d.name for d in DISTRIBUTIONS])
        toolbar.addWidget(self.distribution)
        toolbar.addStretch()
        self.profile_info = label("", "accent")
        toolbar.addWidget(self.profile_info)
        layout.addLayout(toolbar)
        middle = QHBoxLayout()
        terminal, terminal_layout = panel()
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.addWidget(label("   SESSION 01    /    SYNTAX PREVIEW", "accent"))
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setAccessibleName("Terminal preview output")
        self.output.document().setMaximumBlockCount(250)
        terminal_layout.addWidget(self.output, 1)
        middle.addWidget(terminal, 3)
        reference, reference_layout = panel()
        reference.setMinimumWidth(250)
        reference_layout.addWidget(label("SYNTAX//REFERENCE", "accent"))
        reference_layout.addWidget(label("Common across profiles", "muted"))
        reference_layout.addWidget(label("pwd         current directory\nls -a       include hidden\ncd <path>   change directory\ncat <file>  read text\nmkdir <dir> create directory"))
        reference_layout.addSpacing(15)
        reference_layout.addWidget(label("PACKAGE MANAGEMENT", "muted"))
        self.syntax = label("")
        reference_layout.addWidget(self.syntax)
        reference_layout.addStretch()
        reference_layout.addWidget(label("Reference only. Requires a real Linux environment. sudo depends on system setup.", "muted"))
        scroll = QScrollArea()
        scroll.setMaximumWidth(370)
        scroll.setWidgetResizable(True)
        scroll.setWidget(reference)
        middle.addWidget(scroll, 2)
        layout.addLayout(middle, 1)
        self.prompt = label("", "accent")
        layout.addWidget(self.prompt)
        input_row = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type a command to preview the input flow…")
        self.command_input.setAccessibleName("Command input — preview only")
        self.command_input.setMaxLength(4096)
        self.command_input.returnPressed.connect(self.preview_input)
        input_row.addWidget(self.command_input, 1)
        submit = QPushButton("PREVIEW  ↵")
        submit.clicked.connect(self.preview_input)
        input_row.addWidget(submit)
        layout.addLayout(input_row)
        layout.addWidget(label("PROFILE ≠ INSTALLED OS  /  No Linux installation, package execution, or Bash emulation.", "muted"))
        self.distribution.currentIndexChanged.connect(self.update_profile)
        self.update_profile(0)
        return page

    def update_profile(self, index):
        profile = DISTRIBUTIONS[index]
        self.profile_info.setText(f"{profile.shell.upper()}  /  {profile.manager.upper()}")
        self.prompt.setText(f"operator@{profile.slug}:~$")
        self.syntax.setText(f"Refresh / update\n{profile.refresh}\n\nInstall\n{profile.install}\n\nSearch\n{profile.search}")
        self.output.setPlainText(
            "NETWATCH TERMINAL  [version 0.1.0]\n"
            "──────────────────────────────────\n\n"
            "  Your local workspace is ready.\n\n"
            f"  PROFILE    {profile.name}\n"
            f"  FAMILY     {profile.family}\n"
            f"  SHELL      {profile.shell} (reference)\n\n"
            "  [01] Choose a Linux profile above.\n"
            "  [02] Read the syntax reference.\n"
            "  [03] Try the input field below.\n\n"
            "  INTERFACE PREVIEW\n"
            "  Commands are not executed in this version.\n"
            "  The safe command engine is planned for stage 2.\n\n"
            "  No shell processes. No network requests.\n"
        )

    def preview_input(self):
        if self.command_input.text().strip():
            # Do not record input: it may contain secrets, even in a preview.
            self.output.appendPlainText("\n[PREVIEW] Input received. Command execution is not available in stage 1.")
            self.command_input.clear()

    def dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(20)
        self.heading(layout, "00 / SYSTEM OVERVIEW", "SYS//PULSE", "Your local system at a glance. Live monitoring is planned for stage 3.")
        row = QHBoxLayout()
        for title, detail in (("CPU", "Processor utilization"), ("MEMORY", "Used / total RAM"), ("STORAGE", "Free / total disk")):
            frame, box = panel()
            box.addWidget(label(title, "accent"))
            box.addWidget(label("—", "title"))
            box.addWidget(label(detail, "muted"))
            box.addWidget(label("UNAVAILABLE / PREVIEW", "muted"))
            row.addWidget(frame)
        layout.addLayout(row)
        frame, box = panel()
        box.addWidget(label("BUILD//STATUS", "accent"))
        box.addWidget(label("01    Interface and Linux profiles    /    AVAILABLE\n\n02    Safe local commands              /    NEXT\n\n03    Live system metrics              /    PLANNED"))
        box.addWidget(label("No sample percentages or fabricated telemetry are displayed.", "muted"))
        layout.addWidget(frame)
        layout.addStretch()
        return page

    def placeholder_page(self, name, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.heading(layout, "MODULE / PLANNED", name, description)
        frame, box = panel()
        box.addWidget(label("NOT AVAILABLE IN THIS BUILD", "accent"))
        box.addWidget(label("This module is a navigation placeholder. No operations are performed.", "muted"))
        layout.addWidget(frame)
        layout.addStretch()
        return page

    def settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.heading(layout, "07 / PREFERENCES", "SETTINGS", "Interface preview defaults")
        frame, box = panel()
        box.addWidget(label("ACCESSIBILITY", "accent"))
        motion = QCheckBox("Reduce motion — animations are disabled in this build")
        motion.setChecked(True)
        motion.setEnabled(False)
        box.addWidget(motion)
        box.addWidget(label("Language: English. UI strings are separated from the profile model for future localization.\n\nProfiles are session-only. Persistent settings and command history arrive in a later stage.", "muted"))
        layout.addWidget(frame)
        layout.addStretch()
        return page

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        self.buttons[index].setChecked(True)

    def focus_input(self):
        self.navigate(1)
        self.command_input.setFocus()
