from typing import Callable, Dict, List
from functools import reduce

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


def searchInJobField(job: aws.Job, key: str, value: str) -> bool:
    if key not in job.__dict__.keys():
        return False

    attr = getattr(job, key)
    if not isinstance(attr, str) or value not in attr:
        return False

    return True


def searchInJobFields(job: aws.Job, value: str) -> bool:
    keys = job.__dict__.keys()

    for key in keys:
        attr = getattr(job, key)
        if not isinstance(attr, str):
            continue
        if value in attr:
            return True

    return False


def jobFilterFactory(text: str) -> Callable[[aws.Job], bool]:
    filters = text.split(';')

    filtersList = []

    for filterStr in filters:
        if filterStr == '':
            continue

        key = None
        value = None
        try:
            filterStr.index(':')
            keyValue = filterStr.split(':')
            key = keyValue[0].strip()
            value = keyValue[1].strip()

            filtersList.append(lambda job: searchInJobField(job, key, value))
        except ValueError:
            value = filterStr.strip()
            filtersList.append(lambda job: searchInJobFields(job, value))

    def jobFilter(job: aws.Job) -> bool:
        return reduce(lambda x, y: x and y(job), filtersList, True)

    return jobFilter


class TabViewSignals(QObject):
    enable = pyqtSignal(bool)


class JobsSignals(TabViewSignals):
    jobsUpdated = pyqtSignal(list)
    jobRunsUpdated = pyqtSignal(list)


class JobsTab(QWidget):
    signals: JobsSignals

    filterTimer: QTimer
    filterText: str
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

        self.filterTimer = QTimer()
        self.filterTimer.setInterval(500)
        self.filterTimer.timeout.connect(self._refreshTable)
        self.filterText = ''
        self.filter = QLineEdit()
        self.filter.setPlaceholderText(
            'free text | field : value | filter 1; filter 2; ...')
        self.filter.textChanged.connect(self.onFilterChanged)

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

        self._refreshTable()

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
        for jobName, jobRuns in self.jobRuns.items():
            row = next((i for i in range(model.rowCount())
                        if model.item(i, 1).text() == jobName), None)
            # The job has been filtered out
            if row is None:
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

    def _refreshTable(self) -> None:
        jobFilter = jobFilterFactory(self.filterText)
        jobs = [job for job in self.jobs if jobFilter(job)]

        tableModel: QStandardItemModel = self.table.model()

        # Clean up the table
        if tableModel.rowCount() > 0:
            tableModel.removeRows(0, tableModel.rowCount())

        # Fill the job names
        for row in range(len(jobs)):
            job = jobs[row]

            tableModel.setItem(row, 1, QReadOnlyItem(
                text=job.Name, withAutoTooltip=True))

        # Fill the job run defails
        self.populateJobRunDetails()

    def onFilterChanged(self, text: str) -> None:
        if self.filterTimer.isActive():
            self.filterTimer.stop()

        self.filterText = text

        self.filterTimer.start()
