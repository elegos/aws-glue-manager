import dataclasses
from lib import aws
import logging
from os import path
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QModelIndex, QObject, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTableView, QTextEdit, QVBoxLayout, QWidget


def decorateTable(table: QTableView, *columns: Tuple[str, int]) -> None:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([column[0] for column in columns])
    table.setModel(model)
    table.verticalHeader().setVisible(False)

    for i in range(len(columns)):
        table.setColumnWidth(i, columns[i][1])


def getTableModel(columnNames: List[str]) -> QStandardItemModel:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(columnNames)

    return model


class TabViewSignals(QObject):
    enable = pyqtSignal(bool)


class JobsSignals(TabViewSignals):
    jobsUpdated = pyqtSignal(list)
    jobRunsUpdated = pyqtSignal(list)


jobColumns = [
    ('', 16), ('Name', 330),
    ('Last exec date', 146), ('Duration', 80),
    ('Result', 140), ('Error message', 244)
]


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
        self.refreshButton.setIcon(
            QIcon(path.sep.join(['ui', 'icons', 'refresh-cw.svg'])))

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

        fields = [field.name for field in dataclasses.fields(aws.Job)]
        for row in range(len(self.jobs)):
            job = self.jobs[row]

            text = job.Name
            item = QStandardItem(text)
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

            totalRuns = len(jobRuns)
            succeededRuns = len(
                [run for run in jobRuns if run.JobRunState == 'SUCCEEDED'])
            failedRuns = totalRuns - succeededRuns

            if totalRuns == 0:
                continue

            iconsBasePath = ['ui', 'icons']

            iconSvg = 'sun.svg'
            if failedRuns == 1:
                iconSvg = 'cloud.svg'
            elif failedRuns == 2:
                iconSvg = 'cloud-rain.svg'
            elif failedRuns >= 3:
                iconSvg = 'cloud-lightning.svg'

            icon = QIcon(path.sep.join([*iconsBasePath, iconSvg]))
            model.setItem(row, 0, QStandardItem(icon, ''))

            jobRuns.sort(key=lambda run: run.StartedOn)
            lastExecDate = jobRuns[0].StartedOn
            lastDuration = jobRuns[0].ExecutionTime

            hours = int(lastDuration / 60 / 60)
            remainingSeconds = lastDuration - hours * 60 * 60
            minutes = int(remainingSeconds / 60)
            seconds = remainingSeconds - minutes * 60

            model.setItem(row, 2, QStandardItem(
                lastExecDate.strftime('%Y-%m-%d %H:%M:%S')))
            model.setItem(row, 3, QStandardItem(
                f'{hours:02d}:{minutes:02d}:{seconds:02d}'))
            model.setItem(row, 4, QStandardItem(jobRuns[0].JobRunState))
            model.setItem(row, 5, QStandardItem(jobRuns[0].ErrorMessage))


class WorkflowsTab(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()

        self.filter = QLineEdit()
        self.filter.setPlaceholderText(
            'free text | field : value | filter 1; filter 2; ...')

        self.table = QTableView()
        decorateTable(self.table, ('', 16), ('Name', 220),
                      ('Last exec date', 140), ('Last exec duration', 140),
                      ('Last exec result', 140), ('Last jobs executed / total', 230))

        layout.addWidget(self.filter)
        layout.addWidget(self.table, stretch=1)

        self.setLayout(layout)

        # self.table.horizontalHeader().sectionResized.connect(
        #     lambda col, oldW, newW: logging.getLogger().debug(f'{col} {newW}'))
