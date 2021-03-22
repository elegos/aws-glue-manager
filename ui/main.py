import logging
from os import path
from typing import Optional

from PyQt5.QtCore import QSettings, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QHBoxLayout, QLabel,
                             QMainWindow, QPushButton, QWidget)

from lib.config import AWSProfile, ConfigManager
from ui.settings import QSettingsDialog


class MainWindow(QMainWindow):
    config: ConfigManager
    profilePicklist: QComboBox
    settingsButton: QPushButton

    profile: Optional[AWSProfile] = None

    _logger: logging.Logger

    def __init__(self, configManager: ConfigManager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._logger = logging.getLogger()
        self.config = configManager

        self.setWindowTitle('Glue Manager')

        layout = QGridLayout()
        centralWidget = QWidget()
        centralWidget.setLayout(layout)

        self.profilePicklist = QComboBox()
        self.profilePicklist.setMinimumWidth(220)
        self.profilePicklist.currentIndexChanged.connect(
            self.onProfileSelected)
        self.populateProfilePicklist()
        self.onProfileSelected()

        self.settingsButton = QPushButton()
        self.settingsButton.setIcon(
            QIcon(path.sep.join(['ui', 'icons', 'settings.svg'])))
        self.settingsButton.setIconSize(QSize(24, 24))
        self.settingsButton.clicked.connect(self.onSettingsButtonClick)

        topRightLayout = QHBoxLayout()
        topRightLayout.addWidget(QLabel('Profile: '))
        topRightLayout.addWidget(self.profilePicklist)
        topRightLayout.addWidget(self.settingsButton)
        topRightWidget = QWidget()
        topRightWidget.setLayout(topRightLayout)

        layout.addWidget(topRightWidget, 0, 1, 0, -1,
                         Qt.AlignmentFlag.AlignRight)

        self.setCentralWidget(centralWidget)
        self.setMinimumSize(640, 0)

    def populateProfilePicklist(self) -> None:
        self.profilePicklist.clear()
        self.profilePicklist.addItems(
            [profile.label for profile in self.config.profiles])

    def onSettingsButtonClick(self, *args) -> None:
        dialog = QSettingsDialog(configManager=self.config)

        def onClose(*args):
            self.config.save()
            dialog.close()
        dialog.signals.profilesModified.connect(self.onProfilesChanged)

        dialog.accepted.connect(onClose)
        dialog.rejected.connect(onClose)

        dialog.exec_()

    def onProfilesChanged(self) -> None:
        self._logger.info('Profiles updated')
        self.populateProfilePicklist()

    def onProfileSelected(self, *args) -> None:
        self.profile = next(
            (profile for profile in self.config.profiles if profile.label == self.profilePicklist.currentText()), None)

        if self.profile is None:
            self._logger.info(f'Profile selected: <none>')
        else:
            self._logger.info(f'Profile selected: {self.profile.label}')
