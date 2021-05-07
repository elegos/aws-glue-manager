from typing import Callable, Tuple, Union
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
        if len(columns[i]) == 3:
            table.setToolTip(columns[i][2])


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


def searchInObjectField(obj: dict, key: str, value: str) -> bool:
    if key not in obj.keys():
        return False

    attr = obj[key]
    if not isinstance(attr, str) or value.lower() not in attr.lower():
        return False

    return True


def searchInObjectFieldFactory(key: str, value: str) -> Callable[[dict], bool]:
    return lambda obj: searchInObjectField(obj, key, value)


def searchInObjectFields(obj: dict, value: str) -> bool:
    keys = obj.keys()

    for key in keys:
        result = searchInObjectField(obj, key, value)
        if result:
            return True

    return False


def searchInObjectFieldsFactory(value: str) -> Callable[[dict], bool]:
    return lambda obj: searchInObjectFields(obj, value)
