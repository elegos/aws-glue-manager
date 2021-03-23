import logging
import sys

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication

from lib import config, listUtils
from ui.debugWindow import QDebugWindow
from ui.main import MainWindow

infoMode = listUtils.popFlag(sys.argv, '-i', '--info')
debugMode = listUtils.popFlag(sys.argv, '-d', '--debug')

app = QApplication(sys.argv)

configManager = config.ConfigManager()
threadPool = QThreadPool()
window = MainWindow(configManager=configManager, threadPool=threadPool)

if debugMode or infoMode:
    loggingLevel = logging.INFO
    if debugMode:
        loggingLevel = logging.DEBUG

    logDialog = QDebugWindow(loggingLevel=loggingLevel)
    window.closeEvent = lambda _: logDialog.close()

    logDialog.show()
    logDialog.raise_()

window.show()
app.exec_()
