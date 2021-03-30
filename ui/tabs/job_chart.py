import copy
from datetime import datetime, timedelta
from functools import reduce
from typing import Iterator, List

import tzlocal
from PyQt5.QtChart import (QChart, QChartView, QDateTimeAxis, QLineSeries,
                           QValueAxis)
from PyQt5.QtCore import Qt, QPointF
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

        dpuChart = QChart()
        dpuChart.setTitle('DPU usage')
        dpuChart.setAnimationOptions(QChart.SeriesAnimations)
        dpuChart.setAcceptHoverEvents(True)

        dpuSeries = self.getDPUSeries()
        dpuSeries.hovered.connect(self.valueDatetimeChartTooltip)
        dpuChart.addSeries(dpuSeries)

        xAxis = QDateTimeAxis()
        xAxis.setTickCount(18)
        xAxis.setLabelsAngle(60)
        xAxis.setFormat('hh:mm')
        xAxis.setTitleText('Time')

        yAxis = QValueAxis()
        yAxis.setTitleText("DPU usage")

        dpuChart.addAxis(xAxis, Qt.AlignBottom)
        dpuChart.addAxis(yAxis, Qt.AlignLeft)

        dpuSeries.attachAxis(xAxis)
        dpuSeries.attachAxis(yAxis)

        dpuChart.legend().setVisible(True)
        dpuChart.legend().setAlignment(Qt.AlignBottom)

        dpuChartView = QChartView(dpuChart)
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

    def getDPUSeries(self) -> QLineSeries:
        series = QLineSeries()
        series.setName('DPU')

        jobRunsList = copy.deepcopy(self.jobRuns)
        for timestamp in self.timeIterator():
            timestampEnd = timestamp + self.timeInterval
            jobRuns = [run for run in jobRunsList if runInRange(
                run, timestamp, timestampEnd)]

            dpu = reduce(lambda acc, run: acc +
                         run.AllocatedCapacity, jobRuns, 0)
            series.append(int(timestamp.timestamp()*1000), dpu)

            jobRunsList = [
                job for job in jobRunsList if job.CompletedOn is None or job.CompletedOn > timestampEnd]

        return series

    def valueDatetimeChartTooltip(self, point: QPointF) -> None:
        self.coordsLabel.setText(
            'Time ({time}), Value: {value:.02f}'.format(
                time=datetime.fromtimestamp(point.x()/1000).strftime("%H:%M"),
                value=point.y(),
            ))
