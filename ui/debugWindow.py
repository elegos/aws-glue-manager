import logging

from PyQt5.QtWidgets import QDialog, QPlainTextEdit, QVBoxLayout


class QTextEditLogger(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = QPlainTextEdit()
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class QDebugWindow(QDialog, QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Debug log')
        self.setMinimumSize(800, 400)
        logTextBox = QTextEditLogger(level=logging.DEBUG)
        logTextBox.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        layout = QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)
