from typing import Tuple
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QTableView


def decorateTable(table: QTableView, *columns: Tuple[str, int]) -> None:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([column[0] for column in columns])
    table.setModel(model)
    table.verticalHeader().setVisible(False)

    for i in range(len(columns)):
        table.setColumnWidth(i, columns[i][1])


class QReadOnlyItem(QStandardItem):
    def __init__(self, *args) -> None:
        super().__init__(*args)

        self.setEditable(False)
