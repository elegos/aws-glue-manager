import logging
from typing import List, Optional

from PyQt5.QtCore import QSize, Qt, QThreadPool
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QMainWindow, QProgressBar, QPushButton,
                             QTabWidget, QVBoxLayout, QWidget)

from lib import aws
from lib.config import AWSProfile, ConfigManager
from ui.icon import QSVGIcon
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

    apiStack: int

    jobs: List[aws.Job]
    jobRuns: List[aws.JobRun]

    def __init__(self, threadPool: QThreadPool, configManager: ConfigManager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._logger = logging.getLogger()
        self.config = configManager
        self.threadPool = threadPool
        self.apiStack = 0

        self.setWindowTitle('Glue Manager')

        layout = QVBoxLayout()
        centralWidget = QWidget()
        centralWidget.setLayout(layout)

        self.profilePicklist = QComboBox()
        self.profilePicklist.setMinimumWidth(220)
        self.populateProfilePicklist()
        self.profilePicklist.currentIndexChanged.connect(
            self.onProfileSelected)

        self.settingsButton = QPushButton()
        self.settingsButton.setIcon(QSVGIcon('settings.svg'))
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
        self.jobsTab.refreshButton.clicked.connect(self.onJobsDataRequested)
        self.workflowsTab = WorkflowsTab()

        self.tabsView = QTabWidget()
        self.tabsView.addTab(self.jobsTab, 'Jobs')
        self.tabsView.addTab(self.workflowsTab, 'Workflows')

        self.tabsView.currentChanged.connect(self.onTabSelected)

        layout.addWidget(self.tabsView)

        self.setCentralWidget(centralWidget)
        self.setMinimumSize(1024, 900)

        self.statusProgressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.statusProgressBar)
        self.statusBar().showMessage('Ready')

        self.onProfileSelected()

    def populateProfilePicklist(self) -> None:
        self.profilePicklist.clear()
        self.profilePicklist.addItems(
            [profile.label for profile in self.config.settings.profiles])

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

    def onProfileSelected(self, *_) -> None:
        self.profile = next(
            (profile for profile in self.config.settings.profiles if profile.label == self.profilePicklist.currentText()), None)

        if self.profile is not None:
            self._logger.info(f'Profile selected: {self.profile.label}')
            self.onTabSelected(self.tabsView.currentIndex())

    def onJobsDataRequested(self, *_) -> None:
        self.jobsTab.signals.jobsUpdated.emit([])
        self.jobsTab.signals.jobRunsUpdated.emit([])

        self.beforeAWSCall('Downloading jobs data...')
        runnable = aws.getRunnable(aws.getJobs, self.profile)

        runnable.signals.success.connect(self.onJobsDownloaded)
        runnable.signals.success.connect(
            lambda: self.afterAWSCall('Ready'))
        runnable.signals.raised.connect(
            lambda ex: self.onAWSException(ex, True))

        self.threadPool.start(runnable)

    def onTabSelected(self, index) -> None:
        if self.profile is None or self.config.settings.loadDataOnTabChange == False:
            self.statusProgressBar.setVisible(False)
            return

        # jobs
        if index == 0:
            self.onJobsDataRequested()
        elif index == 1:
            # workflows
            # self.beforeAWSCall('Downloading workflows data...')
            pass
        else:
            self.statusBar().showMessage('Ready')
            self.statusProgressBar.setVisible(False)

    def onJobsDownloaded(self, jobs: List[aws.Job]):
        self._logger.info('Jobs downloaded')
        names = [job.Name for job in jobs]
        names.sort()
        self._logger.info('\n'.join(names))

        self.jobsTab.signals.jobsUpdated.emit(jobs)

        self.beforeAWSCall('Downloading jobs run details...',
                           max=len(jobs), stackCount=len(jobs))
        for job in jobs:
            runnable = aws.getRunnable(
                aws.getJobRuns, profile=self.profile, jobName=job.Name)
            runnable.signals.success.connect(self.onJobRunsDownloaded)
            runnable.signals.raised.connect(
                lambda ex: self.onAWSException(ex, True))

            self.threadPool.start(runnable)

    def onJobRunsDownloaded(self, jobRuns: List[aws.JobRun]):
        self.afterAWSCall(incrementProgress=True)
        self.jobsTab.signals.jobRunsUpdated.emit(jobRuns)

    def onAWSException(self, exception: Exception, withAfterAWSCall: bool):
        self._logger.error(exception)
        if withAfterAWSCall:
            self.afterAWSCall(str(exception))

    def beforeAWSCall(self, status: str, max: int = 0, stackCount: int = 1):
        self.apiStack += stackCount

        self.statusBar().showMessage(status)
        self.statusProgressBar.setRange(0, max)
        self.statusProgressBar.setValue(0)
        self.statusProgressBar.setVisible(True)

        self.profilePicklist.setEnabled(False)
        self.tabsView.setEnabled(False)
        self.jobsTab.signals.enable.emit(False)

    def afterAWSCall(self, status: str = 'Ready', incrementProgress: bool = False):
        self.apiStack -= 1

        if self.apiStack < 0:
            self.apiStack = 0

        if incrementProgress:
            self.statusProgressBar.setValue(self.statusProgressBar.value() + 1)

        if self.apiStack == 0:
            self.statusProgressBar.setVisible(False)
            self.statusBar().showMessage(status)

            self.profilePicklist.setEnabled(True)
            self.tabsView.setEnabled(True)
            self.jobsTab.signals.enable.emit(True)

    def closeEvent(self, _) -> None:
        '''When the main window closes, close all the other dialogs'''
        app: QApplication = QApplication.instance()
        if app is not None:
            for widget in app.topLevelWidgets():
                widget.close()
