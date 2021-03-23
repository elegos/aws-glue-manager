from dataclasses import dataclass, field
import dataclasses
import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

import boto3
from boto3_type_annotations.glue import Client as GlueClient
from boto3_type_annotations.glue.client import Client
from boto3_type_annotations.glue.paginator import GetJobs as GetJobsPaginator, GetJobRuns as GetJobRunsPaginator
from botocore.config import Config

from lib.config import AWSProfile


config = Config(
    retries={
        'max_attempts': 10,
        'mode': 'adaptive',
    }
)


@dataclass
class Job:
    Name: str
    Role: str
    CreatedOn: datetime
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
    LastModifiedOn: Optional[datetime] = field(default=None)


@dataclass
class JobRun:
    Id: str
    Attempt: int
    JobName: str
    StartedOn: datetime
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
    NotificationProperty: Dict[str, Any] = field(default_factory=lambda: {})
    CompletedOn: Optional[datetime] = field(default=None)
    TriggerName: Optional[str] = field(default=None)
    PreviousRunId: Optional[str] = field(default=None)
    SecurityConfiguration: Optional[str] = field(default=None)
    LastModifiedOn: Optional[datetime] = field(default=None)


_clients: Dict[str, Client] = {}


def getClient(clientName: str, profile: AWSProfile) -> Any:
    key = hash(profile.accessKey + profile.secretAccessKey)
    if key not in _clients:
        _clients[key] = boto3.client(
            clientName,
            aws_access_key_id=profile.accessKey,
            aws_secret_access_key=profile.secretAccessKey,
            region_name=profile.region,
            config=config,
        )

    return _clients[key]


def getResponseItems(dataclassClass: type, responseField: str, response: dict):
    if responseField not in response:
        logging.getLogger().error(f'{responseField} not in response.')
        logging.getLogger().error({response.keys()})

        return []

    fieldNames = [field.name for field in dataclasses.fields(dataclassClass)]

    return [dataclassClass(**{k: v for k, v in datum.items() if k in fieldNames})
            for datum in response[responseField]]


def getJobs(profile: AWSProfile) -> List[Job]:
    logging.getLogger().info('boto3::get_jobs')
    client: GlueClient = getClient('glue', profile)

    paginator: GetJobsPaginator = client.get_paginator('get_jobs')
    responses = paginator.paginate()
    jobs = []
    for response in responses:
        jobs.extend(getResponseItems(Job, 'Jobs', response))

    return jobs


def getJobRuns(profile: AWSProfile, jobName: str, maxResults: Optional[int] = None) -> List[JobRun]:
    logging.getLogger().info(
        f'boto3::get_job_runs ({jobName}) - max runs: {maxResults}')
    client: GlueClient = getClient('glue', profile)

    if maxResults is not None:
        response = client.get_job_runs(JobName=jobName, MaxResults=maxResults)

        return getResponseItems(JobRun, 'JobRuns', response)

    paginator: GetJobRunsPaginator = client.get_paginator('get_job_runs')
    responses = paginator.paginate()
    runs = []
    for response in responses:
        runs.extend(getResponseItems(JobRun, 'JobRuns', response))

    return runs


class QAWSRunnableSignals(QObject):
    '''AWS API signals
        Attributes:
          success   on request success (arg1: the request's response)
          raised    on request exception (arg1: the request's exception)
    '''

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

    @ pyqtSlot()
    def run(self) -> None:
        try:
            self.signals.success.emit(self.fn(*self.args, **self.kwargs))
        except Exception as ex:
            self.signals.raised.emit(ex)


def getRunnable(fn: callable, *args, **kwargs) -> QAWSRunnable:
    return QAWSRunnable(fn, *args, **kwargs)
