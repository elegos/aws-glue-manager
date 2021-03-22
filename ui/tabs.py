import logging
from typing import List, Tuple
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QLineEdit, QTableView, QTextEdit, QVBoxLayout, QWidget


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


class JobsTab(QWidget):
    filter: QTextEdit
    table: QTableView

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()

        self.filter = QLineEdit()
        self.filter.setPlaceholderText(
            'free text | field : value | filter 1; filter 2; ...')

        self.table = QTableView()
        decorateTable(self.table, ('', 16), ('Name', 220),
                      ('Last exec date', 140), ('Last exec duration', 140),
                      ('Last exec result', 140), ('Last error message', 230))

        layout.addWidget(self.filter)
        layout.addWidget(self.table, stretch=1)

        self.setLayout(layout)


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
