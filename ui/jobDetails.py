from typing import List
from ui.termDescription import QTermDescription
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QTableView, QVBoxLayout, QWidget

from lib import aws, timeUtils
from ui.tabs.common import QReadOnlyItem, decorateTable


class QJobDetails(QWidget):
    job: aws.Job
    jobRuns: List[aws.JobRun]

    runsTable: QTableView

    def __init__(self, job: aws.Job, jobRuns: List[aws.JobRun], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.job = job
        self.jobRuns = jobRuns

        self.setWindowTitle(f'"{job.Name}" job details')
        self.setWindowModality(Qt.WindowModality.WindowModal)

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        connections = ', '.join(
            job.Connections['Connections'] if 'Connections' in job.Connections else [])
        if connections == '':
            connections = 'None'
        td = QTermDescription([
            ('Name', job.Name),
            ('Description', job.Description),
            ('Connections', connections),
            ('IAM Role', job.Role),
            ('Worker Type', job.WorkerType),
            ('Glue Version', job.GlueVersion),
            ('Allocated capacity', str(job.AllocatedCapacity)),
            ('Maximum capacity', str(job.MaxCapacity)),
            ('Timeout', f'{timeUtils.fromTimeToString(minutes=job.Timeout)}'),
        ])
        mainLayout.addWidget(td)

        self.setMinimumSize(QSize(1117, 800))

        self.runsTable = QTableView()
        decorateTable(self.runsTable, ('Id', 150), ('State', 120), ('Error', 220),
                      ('Glue v.', 50), ('Max Capacity', 105), ('Start time', 147), ('End time', 147), ('Duration', 70), ('Timeout', 70))

        mainLayout.addWidget(self.runsTable)
        self.populateJobRuns()

    def populateJobRuns(self):
        model: QStandardItemModel = self.runsTable.model()
        model.removeRows(0, model.rowCount())

        for row in range(len(self.jobRuns)):
            run = self.jobRuns[row]

            startTime = run.CompletedOn.strftime(
                '%Y/%m/%d %H:%M:%S') if run.StartedOn is not None else ''
            endTime = run.CompletedOn.strftime(
                '%Y/%m/%d %H:%M:%S') if run.CompletedOn is not None else ''
            duration = timeUtils.fromTimeToString(seconds=run.ExecutionTime)
            timeout = timeUtils.fromTimeToString(minutes=run.Timeout)

            model.setItem(row, 0, QReadOnlyItem(run.Id, withAutoTooltip=True))
            model.setItem(row, 1, QReadOnlyItem(run.JobRunState))
            model.setItem(row, 2, QReadOnlyItem(
                run.ErrorMessage, withAutoTooltip=True))
            model.setItem(row, 3, QReadOnlyItem(run.GlueVersion))
            model.setItem(row, 4, QReadOnlyItem(str(run.MaxCapacity)))
            model.setItem(row, 5, QReadOnlyItem(startTime))
            model.setItem(row, 6, QReadOnlyItem(endTime))
            model.setItem(row, 7, QReadOnlyItem(duration))
            model.setItem(row, 8, QReadOnlyItem(timeout))
