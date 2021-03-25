from typing import Dict, List

from PyQt5.QtGui import QStandardItemModel

from PyQt5.QtCore import QObject, QSize, QTimer, pyqtSignal
from PyQt5.QtWidgets import (QHBoxLayout, QLineEdit, QPushButton, QTableView,
                             QTextEdit, QVBoxLayout, QWidget)

from lib import aws
from ui.icon import QSVGIcon
from ui.tabs.common import decorateTable, QReadOnlyItem

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

    jobRunDetailsTimer: QTimer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals = JobsSignals()

        self.signals.jobsUpdated.connect(self.updateJobs)
        self.signals.jobRunsUpdated.connect(self.appendJobRuns)

        self.jobs = []
        self.jobRuns = {}

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
            item = QReadOnlyItem(text)
            item.setToolTip(text)
            tableModel.setItem(row, 1, item)

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

            iconSvg = 'sun.svg'
            if failedRuns == 1:
                iconSvg = 'cloud.svg'
            elif failedRuns == 2:
                iconSvg = 'cloud-rain.svg'
            elif failedRuns >= 3:
                iconSvg = 'cloud-lightning.svg'

            icon = QSVGIcon(iconSvg)
            model.setItem(row, 0, QReadOnlyItem(icon, ''))

            lastExecDate = jobRuns[0].StartedOn
            lastDuration = jobRuns[0].ExecutionTime

            hours = int(lastDuration / 60 / 60)
            remainingSeconds = lastDuration - hours * 60 * 60
            minutes = int(remainingSeconds / 60)
            seconds = remainingSeconds - minutes * 60

            model.setItem(row, 2, QReadOnlyItem(
                lastExecDate.strftime('%Y-%m-%d %H:%M:%S')))
            model.setItem(row, 3, QReadOnlyItem(
                f'{hours:02d}:{minutes:02d}:{seconds:02d}'))
            model.setItem(row, 4, QReadOnlyItem(jobRuns[0].JobRunState))

            errorItem = QReadOnlyItem(jobRuns[0].ErrorMessage)
            errorItem.setToolTip(jobRuns[0].ErrorMessage)
            model.setItem(row, 5, errorItem)
