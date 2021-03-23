import logging
from os import path
from typing import List, Optional

from PyQt5.QtCore import QRunnable, QSize, QThreadPool, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QMainWindow,
                             QProgressBar, QPushButton, QTabWidget,
                             QVBoxLayout, QWidget)

from lib.config import AWSProfile, ConfigManager
from lib import aws
from ui.settings import QSettingsDialog
from ui.tabs import JobsTab, WorkflowsTab


class MainWindow(QMainWindow):
    config: ConfigManager
    threadPool: QThreadPool
    profile: Optional[AWSProfile] = None
    _logger: logging.Logger

    profilePicklist: QComboBox
    settingsButton: QPushButton

    statusProgressBar: QProgressBar

    tabsView: QTabWidget
    jobsTab: JobsTab
    workflowsTab: WorkflowsTab

    def __init__(self, threadPool: QThreadPool, configManager: ConfigManager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._logger = logging.getLogger()
        self.config = configManager
        self.threadPool = threadPool

        self.setWindowTitle('Glue Manager')

        layout = QVBoxLayout()
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

        layout.addWidget(topRightWidget, alignment=Qt.AlignmentFlag.AlignRight)

        self.jobsTab = JobsTab()
        self.workflowsTab = WorkflowsTab()

        self.tabsView = QTabWidget()
        self.tabsView.addTab(self.jobsTab, 'Jobs')
        self.tabsView.addTab(self.workflowsTab, 'Workflows')

        self.tabsView.currentChanged.connect(self.onTabSelected)

        layout.addWidget(self.tabsView)

        self.setCentralWidget(centralWidget)
        self.setMinimumSize(940, 0)

        self.statusProgressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.statusProgressBar)
        self.statusBar().showMessage('Ready')

        self.onTabSelected(0)

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
        self.populateProfilePicklist()

    def onProfileSelected(self, *args) -> None:
        self.profile = next(
            (profile for profile in self.config.profiles if profile.label == self.profilePicklist.currentText()), None)

        if self.profile is not None:
            self._logger.info(f'Profile selected: {self.profile.label}')

    def onTabSelected(self, index) -> None:
        if self.profile is None:
            self.statusProgressBar.reset()
            return

        self.statusBar().showMessage('Downloading data...')
        self.statusProgressBar.setRange(0, 0)
        self.statusProgressBar.setValue(0)
        self.statusProgressBar.setVisible(True)

        self.tabsView.setEnabled(False)

        # jobs
        if index == 0:
            self.jobsTab.signals.enable.emit(False)
            runnable = aws.getRunnable(aws.getJobs, self.profile)
            runnable.signals.success.connect(self.onJobsDownloaded)
            runnable.signals.raised.connect(lambda ex: self._logger.error(ex))

            self.threadPool.start(runnable)
        elif index == 1:
            # workflows
            pass
        else:
            self.statusBar().showMessage('Ready')
            self.statusProgressBar.reset()

    def onJobsDownloaded(self, jobs: List[aws.Job]):
        self._logger.info('Jobs downloaded')
        names = [job.Name for job in jobs]
        names.sort()
        self._logger.info('\n'.join(names))

        # TODO get last execution status for each job

        self.statusProgressBar.setVisible(False)
        self.statusBar().showMessage('Ready')
        self.tabsView.setEnabled(True)
        self.jobsTab.signals.enable.emit(True)
