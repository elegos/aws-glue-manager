from dataclasses import dataclass, field
import dataclasses
import logging
from typing import Any, Callable, List
from datetime import datetime
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

import boto3
from boto3_type_annotations.glue import Client as GlueClient
from boto3_type_annotations.glue.paginator import GetJobs as GetJobsPaginator

from lib.config import AWSProfile


@dataclass
class Job:
    Name: str
    Role: str
    CreatedOn: datetime
    LastModifiedOn: datetime
    ExecutionProperty: dict
    Command: dict
    DefaultArguments: dict
    MaxRetries: int
    AllocatedCapacity: int
    Timeout: int
    MaxCapacity: float
    WorkerType: str
    NumberOfWorkers: int
    GlueVersion: str
    Description: str = field(default='')
    SecurityConfiguration: str = field(default='')
    NonOverridableArguments: dict = field(default_factory=lambda: {})
    Connections: dict = field(default_factory=lambda: {})
    NotificationProperty: dict = field(default_factory=lambda: {})


def getClient(clientName: str, profile: AWSProfile) -> Any:
    return boto3.client(
        clientName,
        aws_access_key_id=profile.accessKey,
        aws_secret_access_key=profile.secretAccessKey,
        region_name=profile.region,
    )


def getJobs(profile: AWSProfile) -> List[Job]:
    logging.getLogger().info('boto3::get_jobs')
    client: GlueClient = getClient('glue', profile)

    paginator: GetJobsPaginator = client.get_paginator('get_jobs')
    responses = paginator.paginate()
    jobs = []
    fieldNames = [field.name for field in dataclasses.fields(Job)]
    for response in responses:
        jobs.extend([Job(**{k: v for k, v in job.items() if k in fieldNames})
                    for job in response['Jobs']])

    return jobs


class QAWSRunnableSignals(QObject):
    success = pyqtSignal(object)
    raised = pyqtSignal(Exception)


class QAWSRunnable(QRunnable):
    signals: QAWSRunnableSignals
    fn: Callable
    args: list
    kwargs: dict

    def __init__(self, fn: Callable, *args, **kwargs) -> None:
        super().__init__()

        self.signals = QAWSRunnableSignals()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self) -> None:
        try:
            self.signals.success.emit(self.fn(*self.args, **self.kwargs))
        except Exception as ex:
            self.signals.raised.emit(ex)


def getRunnable(fn: callable, *args, **kwargs) -> QAWSRunnable:
    return QAWSRunnable(fn, *args, **kwargs)
