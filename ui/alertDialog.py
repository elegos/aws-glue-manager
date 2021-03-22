from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class QAlertDialog(QDialog):
    def __init__(self, text: str, title: str = 'Are you sure?', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowTitle(title)
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accepted)
        buttonBox.rejected.connect(self.rejected)

        self.accepted.connect(lambda: self.close())
        self.rejected.connect(lambda: self.close())

        layout = QVBoxLayout()
        layout.addWidget(QLabel(text))
        layout.addWidget(buttonBox)

        self.setLayout(layout)
