import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from netwatch_terminal.app import create_application


@pytest.fixture(scope="session")
def app():
    return create_application([])
