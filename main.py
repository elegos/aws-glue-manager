import sys
from ui.debugWindow import QDebugWindow

from PyQt5.QtWidgets import QApplication

from lib import config
from lib import listUtils
from ui.main import MainWindow

debugMode = listUtils.popFlag(sys.argv, '-d', '--debug')

app = QApplication(sys.argv)

configManager = config.ConfigManager()
window = MainWindow(configManager=configManager)

if debugMode:
    logDialog = QDebugWindow()
    window.closeEvent = lambda _: logDialog.close()

    logDialog.show()
    logDialog.raise_()

window.show()
app.exec_()
