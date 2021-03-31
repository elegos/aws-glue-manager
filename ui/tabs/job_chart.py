import copy
from datetime import datetime, timedelta
from functools import reduce
from typing import Iterator, List, Tuple

import tzlocal
from PyQt5.QtChart import (QChart, QChartView, QDateTimeAxis, QLineSeries,
                           QValueAxis)
from PyQt5.QtCore import QLine, Qt, QPointF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from lib import aws


def runInRange(job: aws.JobRun, rangeStart: datetime, rangeEnd: datetime) -> bool:
    start = job.StartedOn
    end = job.CompletedOn if job.CompletedOn is not None else datetime.now(
        tzlocal.get_localzone())

    return (rangeStart <= start < rangeEnd) or (rangeStart <= end < rangeEnd)


class QJobsChartWindow(QWidget):
    jobRuns: List[aws.JobRun]
    fromDatetime: datetime
    toDatetime: datetime
    timeInterval: timedelta

    coordsLabel: QLabel

    dpuSeries: QLineSeries
    numJobsSeries: QLineSeries

    def __init__(
            self, fromDT: datetime, toDT: datetime,
            jobRuns: List[aws.JobRun],
            interval: timedelta = timedelta(minutes=15),
            *args, **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.fromDatetime = fromDT
        self.toDatetime = toDT
        self.timeInterval = interval

        self.jobRuns = [run for run in jobRuns if run.StartedOn >=
                        fromDT and (run.CompletedOn is None or run.CompletedOn <= toDT)]

        self.setWindowTitle('Job runs recap ({fromDT} / {toDT})'.format(
            fromDT=self.fromDatetime.strftime('%Y-%m-%d %H:%M:%S'),
            toDT=self.toDatetime.strftime('%Y-%m-%d %H:%M:%S'),
        ))

        self.setMinimumSize(1120, 630)

        chart = QChart()
        chart.setTitle('DPU usage')
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setAcceptHoverEvents(True)

        self.dpuSeries, self.numJobsSeries = self.getSeries()
        self.dpuSeries.hovered.connect(self.valueDatetimeChartTooltip)
        self.numJobsSeries.hovered.connect(self.valueDatetimeChartTooltip)

        chart.addSeries(self.dpuSeries)
        chart.addSeries(self.numJobsSeries)

        xAxis = QDateTimeAxis()
        xAxis.setTickCount(18)
        xAxis.setLabelsAngle(60)
        xAxis.setFormat('hh:mm')
        xAxis.setTitleText('Time')

        yDPUAxis = QValueAxis()
        yDPUAxis.setTitleText("DPU usage")

        yNumJobsAxis = QValueAxis()
        yNumJobsAxis.setTitleText("Num jobs")

        chart.addAxis(xAxis, Qt.AlignBottom)
        chart.addAxis(yDPUAxis, Qt.AlignLeft)
        chart.addAxis(yNumJobsAxis, Qt.AlignRight)

        self.dpuSeries.attachAxis(xAxis)
        self.dpuSeries.attachAxis(yDPUAxis)

        self.numJobsSeries.attachAxis(xAxis)
        self.numJobsSeries.attachAxis(yNumJobsAxis)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        dpuChartView = QChartView(chart)
        dpuChartView.setRenderHint(QPainter.Antialiasing)

        self.coordsLabel = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(dpuChartView)
        layout.addWidget(self.coordsLabel)

        self.setLayout(layout)

    def timeIterator(self) -> Iterator[datetime]:
        timestamp = self.fromDatetime
        yield timestamp

        timestamp += self.timeInterval
        while(timestamp <= self.toDatetime):
            yield timestamp
            timestamp += self.timeInterval

    def getSeries(self) -> Tuple[QLineSeries, QLineSeries]:
        self.dpuSeries = QLineSeries()
        self.dpuSeries.setName('DPU')

        self.numJobsSeries = QLineSeries()
        self.numJobsSeries.setName('N. jobs')

        jobRunsList = copy.deepcopy(self.jobRuns)
        for timestamp in self.timeIterator():
            timestampEnd = timestamp + self.timeInterval
            jobRuns = [run for run in jobRunsList if runInRange(
                run, timestamp, timestampEnd)]

            dpu = reduce(lambda acc, run: acc +
                         run.AllocatedCapacity, jobRuns, 0)
            epochMs = int(timestamp.timestamp()*1000)
            self.dpuSeries.append(epochMs, dpu)
            self.numJobsSeries.append(epochMs, len(jobRuns))

            jobRunsList = [
                job for job in jobRunsList if job.CompletedOn is None or job.CompletedOn > timestampEnd]

        return self.dpuSeries, self.numJobsSeries

    def valueDatetimeChartTooltip(self, point: QPointF) -> None:
        x = int(point.x())

        time = datetime.fromtimestamp(x/1000).strftime("%H:%M")
        dpu = min(self.dpuSeries.pointsVector(),
                  key=lambda point: abs(x-point.x())).y()
        jobs = min(self.numJobsSeries.pointsVector(),
                   key=lambda point: abs(x-point.x())).y()

        self.coordsLabel.setText(
            'Time ({time}), DPU: {dpu}, Job runs: {jobRuns}'.format(
                time=time,
                dpu=0 if dpu is None else int(dpu),
                jobRuns=0 if jobs is None else int(jobs),
            ))
