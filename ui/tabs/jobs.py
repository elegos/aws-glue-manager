from typing import Dict, List

from PyQt5.QtCore import QModelIndex, QObject, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QHBoxLayout, QLineEdit, QPushButton, QTableView,
                             QTextEdit, QVBoxLayout, QWidget)

from lib import aws, timeUtils
from ui.icon import QSVGIcon
from ui.jobDetails import QJobDetails
from ui.tabs.common import QReadOnlyItem, decorateTable

jobColumns = [
    ('', 16), ('Name', 330),
    ('Last execution', 146), ('Duration', 80),
    ('Result', 140), ('Error message', 244)
]


class TabViewSignals(QObject):
    enable = pyqtSignal(bool)


class JobsSignals(TabViewSignals):
    jobsUpdated = pyqtSignal(list)
    jobRunsUpdated = pyqtSignal(list)


class JobsTab(QWidget):
    signals: JobsSignals

    filter: QTextEdit
    table: QTableView
    refreshButton: QPushButton

    jobs: List[aws.Job]
    jobRuns: Dict[str, List[aws.JobRun]]
    jobDialogs: Dict[str, QJobDetails]

    jobRunDetailsTimer: QTimer

    statusIcons: Dict[str, QSVGIcon]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals = JobsSignals()

        self.signals.jobsUpdated.connect(self.updateJobs)
        self.signals.jobRunsUpdated.connect(self.appendJobRuns)

        self.jobs = []
        self.jobRuns = {}
        self.jobDialogs = {}

        self.statusIcons = {
            'sunny': QSVGIcon('sun.svg'),
            'cloudy': QSVGIcon('cloud.svg'),
            'rainy': QSVGIcon('cloud-rain.svg'),
            'thunders': QSVGIcon('cloud-lightning'),
        }

        self.jobRunDetailsTimer = QTimer()
        self.jobRunDetailsTimer.timeout.connect(self.populateJobRunDetails)

        layout = QVBoxLayout()

        filterWidget = QWidget()
        filterLayout = QHBoxLayout()

        self.filter = QLineEdit()
        self.filter.setPlaceholderText(
            'free text | field : value | filter 1; filter 2; ...')

        self.refreshButton = QPushButton()
        self.refreshButton.setIcon(QSVGIcon('refresh-cw.svg'))
        self.refreshButton.setIconSize(QSize(18, 18))

        filterLayout.addWidget(self.filter)
        filterLayout.addWidget(self.refreshButton)
        filterWidget.setLayout(filterLayout)

        self.table = QTableView()
        decorateTable(self.table, *jobColumns)

        self.table.doubleClicked.connect(self.onTableDoubleClick)

        layout.addWidget(filterWidget)
        layout.addWidget(self.table, stretch=1)

        self.setLayout(layout)

        self.signals.enable.connect(self.setEnableStatus)

    def setEnableStatus(self, enabled: bool):
        if enabled:
            self.refreshButton.setEnabled(True)
        else:
            self.refreshButton.setEnabled(False)

    def updateJobs(self, jobs: List[aws.Job]):
        # Reset the opened dialogs
        self.jobDialogs = {}

        self.jobs = jobs
        if len(jobs) == 0:
            self.jobRuns = {}

        self.showJobs()

    def showJobs(self):
        tableModel: QStandardItemModel = self.table.model()

        if tableModel.rowCount() > 0:
            tableModel.removeRows(0, tableModel.rowCount())

        for row in range(len(self.jobs)):
            job = self.jobs[row]

            text = job.Name
            tableModel.setItem(row, 1, QReadOnlyItem(
                text=text, withAutoTooltip=True))

    def appendJobRuns(self, jobRuns: List[aws.JobRun]):
        if self.jobRunDetailsTimer.isActive():
            self.jobRunDetailsTimer.stop()

        for run in jobRuns:
            if run.JobName not in self.jobRuns:
                self.jobRuns[run.JobName] = []
            if next((jr for jr in self.jobRuns[run.JobName] if jr.Id == run.Id), None) is None:
                self.jobRuns[run.JobName].append(run)

        self.jobRunDetailsTimer.start(1000)

    def populateJobRunDetails(self):
        model = self.table.model()
        rowsCount = model.rowCount()
        for row in range(rowsCount):
            jobName = model.itemData(model.index(row, 1)).get(0)

            jobRuns = self.jobRuns[jobName] if jobName in self.jobRuns else None
            if jobRuns == None:
                continue

            jobRuns.sort(key=lambda run: run.StartedOn, reverse=True)
            jobRuns = jobRuns[0:5]

            totalRuns = len(jobRuns)
            succeededRuns = len(
                [run for run in jobRuns if run.JobRunState == 'SUCCEEDED'])
            failedRuns = totalRuns - succeededRuns

            if totalRuns == 0:
                continue

            icon = self.statusIcons['sunny']
            if failedRuns == 1:
                icon = self.statusIcons['cloudy']
            elif failedRuns == 2:
                icon = self.statusIcons['rainy']
            elif failedRuns >= 3:
                icon = self.statusIcons['thunders']

            model.setItem(row, 0, QReadOnlyItem(icon, False, ''))

            lastExecDate = jobRuns[0].StartedOn
            lastDuration = jobRuns[0].ExecutionTime

            model.setItem(row, 2, QReadOnlyItem(
                lastExecDate.strftime('%Y-%m-%d %H:%M:%S')))
            model.setItem(row, 3, QReadOnlyItem(
                timeUtils.fromTimeToString(seconds=lastDuration)))
            model.setItem(row, 4, QReadOnlyItem(jobRuns[0].JobRunState))

            errorItem = QReadOnlyItem(
                jobRuns[0].ErrorMessage, withAutoTooltip=True)
            errorItem.setToolTip(jobRuns[0].ErrorMessage)
            model.setItem(row, 5, errorItem)

    def onTableDoubleClick(self, index: QModelIndex):
        job = self.jobs[index.row()]
        jobRuns = self.jobRuns[job.Name] if job.Name in self.jobRuns else []

        if job.Name in self.jobDialogs:
            del(self.jobDialogs[job.Name])

        detailsWindow = QJobDetails(job, jobRuns)
        detailsWindow.show()
        self.jobDialogs[job.Name] = detailsWindow