from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from lib import aws


class QJobDetails(QWidget):
    job: aws.Job
    jobRuns: List[aws.JobRun]

    def __init__(self, job: aws.Job, jobRuns: List[aws.JobRun], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.job = job
        self.jobRuns = jobRuns

        self.setWindowTitle(f'"{job.Name}" job details')
        self.setWindowModality(Qt.WindowModality.WindowModal)

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(QLabel(f'Name: {job.Name}'))
