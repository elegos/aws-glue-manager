from ui.icon import QSVGIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTableView, QVBoxLayout, QWidget
from logging import Logger, getLogger

from ui.tabs.common import TabViewSignals, decorateTable


class WorkflowsTabSignals(TabViewSignals):
    pass


class WorkflowsTab(QWidget):
    signals: WorkflowsTabSignals
    logger: Logger

    filter: QLineEdit
    refreshButton: QPushButton

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals = WorkflowsTabSignals()
        self.logger = getLogger()

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
        decorateTable(self.table, ('', 16), ('Name', 220),
                      ('Last exec date', 140), ('Last exec duration', 140),
                      ('Last exec result', 140), ('Last jobs executed / total', 230))

        layout.addWidget(filterWidget)
        layout.addWidget(self.table, stretch=1)

        self.setLayout(layout)

        # events
        self.signals.enable.connect(self.setEnableState)
        self.refreshButton.clicked.connect(self.onRefreshButtonClick)

    def setEnableState(self, state: bool):
        self.logger.debug(
            f'Setting workflows tab enabled: {"enabled" if state else "disabled"}'
        )

        self.filter.setEnabled(state)
        self.refreshButton.setEnabled(state)

    def onRefreshButtonClick(self, _: bool):
        self.logger.info('Refreshing workflows table')
