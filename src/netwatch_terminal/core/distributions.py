"""Informational Linux profiles. These strings are never executed."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Distribution:
    name: str
    slug: str
    family: str
    shell: str
    manager: str
    refresh: str
    install: str
    search: str


DISTRIBUTIONS = (
    Distribution("Ubuntu", "ubuntu", "Debian", "bash", "apt", "sudo apt update", "sudo apt install <package>", "apt search <package>"),
    Distribution("Debian", "debian", "Debian", "bash", "apt", "sudo apt update", "sudo apt install <package>", "apt search <package>"),
    Distribution("Fedora", "fedora", "Red Hat", "bash", "dnf", "sudo dnf check-update", "sudo dnf install <package>", "dnf search <package>"),
    Distribution("Arch Linux", "arch", "Arch", "bash", "pacman", "sudo pacman -Syu", "sudo pacman -S <package>", "pacman -Ss <package>"),
    Distribution("Kali Linux", "kali", "Debian", "zsh", "apt", "sudo apt update", "sudo apt install <package>", "apt search <package>"),
    Distribution("openSUSE", "opensuse", "SUSE", "bash", "zypper", "sudo zypper refresh", "sudo zypper install <package>", "zypper search <package>"),
    Distribution("Alpine", "alpine", "Alpine", "ash", "apk", "sudo apk update", "sudo apk add <package>", "apk search <package>"),
)
