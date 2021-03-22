import sys

from PyQt5.QtWidgets import QApplication

from lib import config
from ui.main import MainWindow

app = QApplication(sys.argv)

configManager = config.ConfigManager()
window = MainWindow(configManager=configManager)
window.show()

app.exec_()
