from functools import reduce
from lib import aws
import math
from logging import Logger, getLogger
from typing import Callable, Dict, List

from PyQt5.QtCore import QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QCheckBox, QHBoxLayout, QLineEdit, QPushButton, QTableView,
                             QVBoxLayout, QWidget)

from lib.aws.workflows import Workflow
from ui.icon import QSVGIcon
from ui.tabs.common import QReadOnlyItem, TabViewSignals, decorateTable, searchInObjectFieldFactory, searchInObjectFieldsFactory


class WorkflowsTabSignals(TabViewSignals):
    workflowsUpdated = pyqtSignal(list)
    workflowsRunsUpdated = pyqtSignal(list)


def workflowFilterFactory(text: str) -> Callable[[aws.Workflow], bool]:
    filters = list(map(lambda x: x.strip(), text.split(';')))

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

            filtersList.append(searchInObjectFieldFactory(key, value))
        except ValueError:
            value = filterStr.strip()
            filtersList.append(searchInObjectFieldsFactory(value))

    def workflowFilter(flow: aws.Workflow) -> bool:
        lastRun = flow.LastRun

        obj = {
            'Name': flow.Name,
            'Last exec result': lastRun.Status if lastRun is not None else None,
        }

        return reduce(lambda x, y: x and y(obj), filtersList, True)

    return workflowFilter


class WorkflowsTab(QWidget):
    # Cross attributes
    signals: WorkflowsTabSignals
    logger: Logger

    # Class attributes
    workflows: List[Workflow]
    statusIcons: Dict[str, QSVGIcon]
    filterText: str
    filterTimer: QTimer

    # UI elements
    filter: QLineEdit
    failedIfNotAllExecuted: QCheckBox
    refreshButton: QPushButton

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals = WorkflowsTabSignals()
        self.logger = getLogger()
        self.workflows = []
        self.filterText = ''
        self.statusIcons = {
            'play': QSVGIcon('play.svg'),
            'stop': QSVGIcon('square.svg'),
            'pause': QSVGIcon('pause.svg'),
            'sunny': QSVGIcon('sun.svg'),
            'thunders': QSVGIcon('cloud-lightning'),
        }

        layout = QVBoxLayout()

        filterWidget = QWidget()
        filterLayout = QHBoxLayout()

        self.filterTimer = QTimer()
        self.filterTimer.setInterval(500)
        self.filterTimer.setSingleShot(True)
        self.filterTimer.timeout.connect(self._refreshTable)

        self.failedIfNotAllExecuted = QCheckBox('Failed if not all executed')
        self.failedIfNotAllExecuted.toggled.connect(self._refreshTable)

        self.filter = QLineEdit()
        self.filter.setPlaceholderText(
            'free text | field : value | filter 1; filter 2; ...')
        self.filter.textChanged.connect(self.onFilterChanged)

        self.refreshButton = QPushButton()
        self.refreshButton.setIcon(QSVGIcon('refresh-cw.svg'))
        self.refreshButton.setIconSize(QSize(18, 18))

        filterLayout.addWidget(self.filter)
        filterLayout.addWidget(self.failedIfNotAllExecuted)
        filterLayout.addWidget(self.refreshButton)
        filterWidget.setLayout(filterLayout)

        self.table = QTableView()
        decorateTable(
            self.table, ('', 10), ('Name', 220),
            ('Last exec date', 140), ('Last exec duration', 120),
            ('Last exec result', 140), ('Su / Fa / Ti / St / Ru / To', 280,
                                        '[Su]cceded / [Fa]iled / [Ti]meout / [St]opped / [Ru]nning / [To]tal')
        )

        layout.addWidget(filterWidget)
        layout.addWidget(self.table, stretch=1)

        self.setLayout(layout)

        # events
        self.signals.enable.connect(self.setEnableState)
        self.signals.workflowsUpdated.connect(self.onWorkflowsListUpdate)

    def setEnableState(self, state: bool):
        self.logger.debug(
            f'Setting workflows tab enabled: {"enabled" if state else "disabled"}'
        )

        self.filter.setEnabled(state)
        self.refreshButton.setEnabled(state)

    def onWorkflowsListUpdate(self, workflows: List[Workflow]) -> None:
        self.workflows = workflows
        self._refreshTable()

    def getFilteredWorkflows(self):
        rawFilters = self.filterText
        workflowFilter = workflowFilterFactory(rawFilters)

        return [flow for flow in self.workflows if workflowFilter(flow)]

    def _refreshTable(self):
        workflows = self.getFilteredWorkflows()
        tableModel: QStandardItemModel = self.table.model()

        # Clean up the table
        if tableModel.rowCount() > 0:
            tableModel.removeRows(0, tableModel.rowCount())

        # Fill the data
        statusIcon = {
            'RUNNING': self.statusIcons['play'],
            'COMPLETED': self.statusIcons['sunny'],
            'STOPPING': self.statusIcons['pause'],
            'STOPPED': self.statusIcons['stop'],
            'ERROR': self.statusIcons['thunders'],
        }
        timeFormat = '%Y-%m-%d %H:%M:%S'
        for row in range(0, len(workflows)):
            flow = workflows[row]
            tableModel.setItem(row, 1, QReadOnlyItem(flow.Name, True))

            if flow.LastRun is not None:
                icon = None
                lastRun = flow.LastRun
                startDate = lastRun.StartedOn.strftime(timeFormat)
                execDuration = ''
                if lastRun.CompletedOn is not None:
                    execDuration = (lastRun.CompletedOn -
                                    lastRun.StartedOn).total_seconds()
                    hours = math.floor(execDuration / 60 / 60)
                    minutes = math.floor(execDuration / 60) - (hours * 60)
                    seconds = int(execDuration - hours *
                                  60 * 60 - minutes * 60)
                    execDuration = f'{hours:02d}:{minutes:02d}:{seconds:02d}'

                icon = statusIcon[lastRun.Status]
                executions = 'N/A'
                if lastRun.Statistics is not None:
                    executions = 'Su: {succeded:02d} / Fa: {failed:02d} / Ti: {timeout:02d} / St: {stopped:02d} / Ru: {running:02d} / To: {total:02d}'.format(
                        succeded=lastRun.Statistics.SucceededActions,
                        failed=lastRun.Statistics.FailedActions,
                        timeout=lastRun.Statistics.TimeoutActions,
                        stopped=lastRun.Statistics.StoppedActions,
                        running=lastRun.Statistics.RunningActions,
                        total=lastRun.Statistics.TotalActions,
                    )
                    if lastRun.CompletedOn is not None \
                            and (
                                lastRun.Statistics.FailedActions > 0
                                or lastRun.Statistics.StoppedActions > 0
                                or lastRun.Statistics.TimeoutActions > 0
                                or (
                                    self.failedIfNotAllExecuted.isChecked()
                                    and lastRun.Statistics.SucceededActions < lastRun.Statistics.TotalActions
                                )
                            ):
                        icon = statusIcon['ERROR']

                tableModel.setItem(row, 0, QReadOnlyItem(icon, False, ''))
                tableModel.setItem(row, 2, QReadOnlyItem(startDate))
                tableModel.setItem(row, 3, QReadOnlyItem(execDuration))
                tableModel.setItem(row, 4, QReadOnlyItem(lastRun.Status, True))
                tableModel.setItem(row, 5, QReadOnlyItem(executions, True))

    def onFilterChanged(self, text: str) -> None:
        if self.filterTimer.isActive():
            self.filterTimer.stop()

        self.filterText = text

        self.filterTimer.start()
