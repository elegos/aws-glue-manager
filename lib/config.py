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


class InvalidSettingException(Exception):
    def __init__(self, name: str, sType: type, expectedType: Optional[type]):
        expectedType = str(
            expectedType) if expectedType is not None else 'None'
        super().__init__(
            f'Unexpected setting: "{name}" (found: {str(sType)}, expected: {expectedType})')


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

    def asDict(self):
        return {
            'profiles': [profile.asDict() for profile in self.profiles]
        }


class ConfigManager:
    configRoot: str = ''
    _settings: Settings

    def __init__(self, appId=const.appId):
        '''
        Raise config.UnsupportedPlatformException
        '''
        super().__setattr__('_settings', Settings())

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
            self._settings = Settings()

            return

        with open(configPath) as fHandler:
            settings = Settings()
            kwargs = json.load(fHandler)
            if kwargs is not None:
                settings.loadFromArgs(**kwargs)

            self._settings = settings

    def save(self) -> None:
        self._createConfigDir()
        text = json.dumps(self._settings.asDict())

        with open(self._configPath(), 'w') as fHandler:
            fHandler.write(text)

    def deleteConfig(self) -> None:
        try:
            shutil.rmtree(path.dirname(self._configPath()))
        finally:
            pass

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except Exception:
            pass

        settings = super().__getattribute__('_settings')
        if settings is not None and hasattr(settings, name):
            return getattr(settings, name)

        return None

    def __setattr__(self, name: str, value: Any) -> None:
        '''
        Raise config.InvalidSettingException
        '''

        if hasattr(self, name):
            return super().__setattr__(name, value)

        templateSettings = Settings()
        expectedType = type(templateSettings[name]) if hasattr(
            templateSettings, name) else None

        if expectedType is not None and isinstance(value, expectedType):
            self._settings[name] = value

        raise InvalidSettingException(name, type(value), expectedType)
