import dataclasses
import logging
from typing import Any, Callable, Dict, List, Tuple
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from boto3_type_annotations.glue.client import Client
from botocore.config import Config

from lib.config import AWSProfile
import boto3


_clients: Dict[str, Client] = {}


config = Config(
    retries={
        'max_attempts': 10,
        'mode': 'adaptive',
    }
)


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


def dataclassPostInitializer(fieldTuples: List[Tuple[str, type]]) -> Callable[[Any], None]:
    def initializer(self: Any) -> None:
        for fieldTuple in fieldTuples:
            field, fType = fieldTuple
            data = getattr(self, field)
            if data is not None:
                setattr(self, field, initClassFromArgs(
                    fType, data
                ))

    return initializer


def initClassFromArgs(classType: type, data: dict):
    fieldNames = [field.name for field in dataclasses.fields(classType)]

    return classType(**{key: value for key, value in data.items() if key in fieldNames})


def getResponseItems(dataclassClass: type, responseField: str, response: dict):
    if responseField not in response:
        logging.getLogger().error(f'{responseField} not in response.')
        logging.getLogger().error({response.keys()})

        return []

    return [initClassFromArgs(dataclassClass, datum) for datum in response[responseField]]


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

    @pyqtSlot()
    def run(self) -> None:
        try:
            self.signals.success.emit(self.fn(*self.args, **self.kwargs))
        except Exception as ex:
            self.signals.raised.emit(ex)


def getRunnable(fn: callable, *args, **kwargs) -> QAWSRunnable:
    return QAWSRunnable(fn, *args, **kwargs)
