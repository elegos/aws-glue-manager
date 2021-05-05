from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import List, Optional

from boto3_type_annotations.glue.client import Client

from lib.aws.common import dataclassPostInitializer, getClient, getResponseItems
from lib.config import AWSProfile


@dataclass
class WorkflowGraph:
    pass


@dataclass
class WorkflowRunStatistics:
    TotalActions: int
    TimeoutActions: int
    FailedActions: int
    StoppedActions: int
    SucceededActions: int
    RunningActions: int


@dataclass
class WorkflowRun:
    Name: str
    WorkflowRunId: str
    WorkflowRunProperties: dict
    Status: str
    StartedOn: datetime

    PreviousRunId: Optional[str] = field(default=None)
    CompletedOn: Optional[datetime] = field(default=None)
    ErrorMessage: Optional[str] = field(default=None)
    Statistics: Optional[WorkflowRunStatistics] = field(default=None)
    Graph: Optional[WorkflowGraph] = field(default=None)

    def __post_init__(self):
        dataclassPostInitializer([
            ('Statistics', WorkflowRunStatistics),
            ('Graph', WorkflowGraph),
        ])


@dataclass
class Workflow:
    Name: str
    CreatedOn: datetime
    MaxConcurrentRuns: int

    DefaultRunProperties: Optional[dict] = field(default=None)
    Description: Optional[str] = field(default=None)
    LastModifiedOn: Optional[datetime] = field(default=None)
    LastRun: Optional[WorkflowRun] = field(default=None)
    Graph: Optional[WorkflowGraph] = field(default=None)

    def __post_init__(self):
        dataclassPostInitializer([
            ('Graph', WorkflowGraph),
            ('LastRun', WorkflowRun),
        ])(self)


def getWorkflowsList(profile: AWSProfile) -> List[str]:
    logger = logging.getLogger()
    logger.info('boto3::list_workflows')
    client: Client = getClient('glue', profile)

    logger.debug('boto3::list_workflows: getting list of workflow names')
    # Workflow names
    kwargs = {'MaxResults': 25}
    workflowNames: List[str] = []
    while True:
        response = client.list_workflows(**kwargs)
        workflowNames.extend(response['Workflows'])

        if 'NextToken' not in response or response['NextToken']:
            break
        kwargs.update({'NextToken': response['NextToken']})

    logger.debug('boto3::list_workflows: getting workflow batch details')
    response = client.batch_get_workflows(
        Names=workflowNames, IncludeGraph=True
    )

    return getResponseItems(Workflow, 'Workflows', response)
