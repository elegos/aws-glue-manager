from typing import Tuple, Union
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QTableView


class TabViewSignals(QObject):
    enable = pyqtSignal(bool)


def decorateTable(table: QTableView, *columns: Tuple[str, int]) -> None:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([column[0] for column in columns])
    table.setModel(model)
    table.verticalHeader().setVisible(False)

    for i in range(len(columns)):
        table.setColumnWidth(i, columns[i][1])


class QReadOnlyItem(QStandardItem):
    withAutoTooltip: bool

    def __init__(self, text: Union[str, QIcon], withAutoTooltip: bool = False, *args) -> None:
        if isinstance(text, QIcon):
            super().__init__(text, *args)
            return

        super().__init__(*args)

        self.setEditable(False)
        self.withAutoTooltip = withAutoTooltip
        self.setText(text)

    def setText(self, text: str) -> None:
        super().setText(text)

        if self.withAutoTooltip:
            self.setToolTip(text)
