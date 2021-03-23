import logging
from os import path
from typing import List, Tuple
from PyQt5.QtCore import QObject, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTableView, QTextEdit, QVBoxLayout, QWidget


def decorateTable(table: QTableView, *columns: Tuple[str, int]) -> None:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([column[0] for column in columns])
    table.setModel(model)

    for i in range(len(columns)):
        table.setColumnWidth(i, columns[i][1])


def getTableModel(columnNames: List[str]) -> QStandardItemModel:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(columnNames)

    return model


class TabViewSignals(QObject):
    enable = pyqtSignal(bool)


class JobsTab(QWidget):
    signals: TabViewSignals

    filter: QTextEdit
    table: QTableView
    refreshButton: QPushButton

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals = TabViewSignals()

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
        decorateTable(self.table, ('', 16), ('Name', 220),
                      ('Last exec date', 140), ('Last exec duration', 140),
                      ('Last exec result', 140), ('Last error message', 230))

        layout.addWidget(filterWidget)
        layout.addWidget(self.table, stretch=1)

        self.setLayout(layout)

        self.signals.enable.connect(self.setEnableStatus)

    def setEnableStatus(self, enabled: bool):
        if enabled:
            self.refreshButton.setEnabled(True)
        else:
            self.refreshButton.setEnabled(False)


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
