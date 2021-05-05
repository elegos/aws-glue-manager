import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from boto3_type_annotations.glue.client import Client as GlueClient
from boto3_type_annotations.glue.paginator import \
    GetJobRuns as GetJobRunsPaginator
from boto3_type_annotations.glue.paginator import GetJobs as GetJobsPaginator

from lib.aws.common import getClient, getResponseItems
from lib.config import AWSProfile


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
    LogGroupName: str
    GlueVersion: str
    WorkerType: str = field(default='')
    ErrorMessage: str = field(default='')
    PredecessorRuns: list = field(default_factory=[])
    Arguments: Dict[str, str] = field(default_factory=lambda: {})
    NotificationProperty: Dict[str, Any] = field(default_factory=lambda: {})
    NumberOfWorkers: Optional[int] = field(default=None)
    CompletedOn: Optional[datetime] = field(default=None)
    TriggerName: Optional[str] = field(default=None)
    PreviousRunId: Optional[str] = field(default=None)
    SecurityConfiguration: Optional[str] = field(default=None)
    LastModifiedOn: Optional[datetime] = field(default=None)


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
    responses = paginator.paginate(JobName=jobName)
    runs = []
    for response in responses:
        runs.extend(getResponseItems(JobRun, 'JobRuns', response))

    return runs
