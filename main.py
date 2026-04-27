#!/usr/bin/env python
import sys

from PySide6.QtWidgets import QApplication

from modules.utils import __version__
from modules.gui import MainWindow, APP_ICON

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(APP_ICON)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
