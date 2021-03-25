import json
import pathlib
import platform
import shutil
from dataclasses import dataclass, field
from os import path, getenv
from os.path import expanduser
from typing import Any, List, Optional

from lib import const, encryption


class UnsupportedPlatformException(Exception):
    def __init__(self) -> None:
        super().__init__(f'Unsupported platform: {platform.system()}')


@dataclass
class AWSProfile:
    label: str = field(default='')
    region: str = field(default='')
    accessKey: str = field(default='')
    secretAccessKey: str = field(default='')

    def loadFromArgs(self, **kwargs) -> None:
        encdec = encryption.EncDec()
        for key in self.__dict__.keys():
            if key in kwargs:
                value = kwargs[key]
                if key == 'secretAccessKey':
                    value = encdec.decrypt(value)
                setattr(self, key, value)

    def asDict(self):
        encdec = encryption.EncDec()
        result = {}
        for key, value in self.__dict__.items():
            if key == 'secretAccessKey':
                value = encdec.encrypt(value)
            result[key] = value

        return result


@dataclass
class Settings:
    loadDataOnTabChange: bool = field(default=False)
    profiles: List[AWSProfile] = field(default_factory=lambda: [])

    def loadFromArgs(self, **kwargs) -> None:
        if 'profiles' in kwargs and isinstance(kwargs['profiles'], list):
            for profileData in kwargs['profiles']:
                profile = AWSProfile()
                profile.loadFromArgs(**profileData)
                self.profiles.append(profile)
        if 'loadDataOnTabChange' in kwargs and isinstance(kwargs['loadDataOnTabChange'], bool):
            self.loadDataOnTabChange = kwargs['loadDataOnTabChange']

    def asDict(self):
        return {
            'profiles': [profile.asDict() for profile in self.profiles],
            'loadDataOnTabChange': self.loadDataOnTabChange,
        }


class ConfigManager:
    configRoot: str = ''
    settings: Settings
    settings: Settings

    def __init__(self, appId=const.appId):
        '''
        Raise config.UnsupportedPlatformException
        '''
        self.settings = Settings()

        sysName = platform.system().lower()
        if sysName == 'linux':
            self.configRoot = expanduser(f'~/.config/{appId}')
        elif sysName == 'darwin':
            self.configRoot = expanduser(
                f'~/Library/Application Support/{appId}')
        elif sysName == 'windows':
            self.configRoot = path.sep.join([getenv('APPDATA'), appId])
        else:
            raise UnsupportedPlatformException()

        self.load()

    def __del__(self):
        self.save()

    def _createConfigDir(self) -> None:
        pathlib.Path(self.configRoot).mkdir(parents=True, exist_ok=True)

    def _configPath(self) -> str:
        return path.sep.join([self.configRoot, 'configuration'])

    def load(self):
        self._createConfigDir()
        configPath = self._configPath()

        if not path.exists(configPath):
            self.settings = Settings()

            return

        with open(configPath) as fHandler:
            settings = Settings()
            kwargs = json.load(fHandler)
            if kwargs is not None:
                settings.loadFromArgs(**kwargs)

            self.settings = settings

    def save(self) -> None:
        self._createConfigDir()
        text = json.dumps(self.settings.asDict())

        with open(self._configPath(), 'w') as fHandler:
            fHandler.write(text)

    def deleteConfig(self) -> None:
        try:
            shutil.rmtree(path.dirname(self._configPath()))
        finally:
            pass
