from dataclasses import dataclass, field
import dataclasses
import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

import boto3
from boto3_type_annotations.glue import Client as GlueClient
from boto3_type_annotations.glue.paginator import GetJobs as GetJobsPaginator, GetJobRuns as GetJobRunsPaginator

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


class JobRun:
    Id: str
    Attempt: int
    JobName: str
    StartedOn: datetime
    LastModifiedOn: datetime
    CompletedOn: Optional[datetime] = field(default=None)
    JobRunState: str
    AllocatedCapacity: int
    ExecutionTime: int  # seconds
    Timeout: int  # minutes
    MaxCapacity: float
    WorkerType: str
    NumberOfWorkers: int
    LogGroupName: str
    GlueVersion: str
    ErrorMessage: str = field(default='')
    PredecessorRuns: list = field(default_factory=[])
    Arguments: Dict[str, str] = field(default_factory=lambda: {})
    NotificationProperty: Dict[str, Any] = field(default_factory={})
    TriggerName: Optional[str] = field(default=None)
    PreviousRunId: Optional[str] = field(default=None)
    SecurityConfiguration: Optional[str] = field(default=None)


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


def getJobRuns(profile: AWSProfile, jobName: str):
    logging.getLogger().info('boto3::get_job_runs')
    client: GlueClient = getClient('glue', profile)

    paginator: GetJobRunsPaginator = client.get_paginator('get_job_runs')
    responses = paginator.paginate()
    runs = []
    fieldNames = [field.name for field in dataclasses.felds(JobRun)]
    for response in responses:
        runs.extend([Job(**{k: v for k, v in job.items() if k in fieldNames})
                    for job in response['JobRuns']])


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
