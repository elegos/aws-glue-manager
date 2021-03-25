from PyQt5.QtWidgets import QLineEdit, QTableView, QVBoxLayout, QWidget

from ui.tabs.common import decorateTable


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
