from os import path
from shutil import rmtree
from unittest import TestCase

from lib import const
from lib import config


class ConfigManagerTestCase(TestCase):
    manager: config.ConfigManager

    def getManager(self) -> config.ConfigManager:
        return self.manager

    def setUp(self) -> None:
        super().setUp()
        self.manager = config.ConfigManager(appId=const.testAppId)

    def tearDown(self) -> None:
        super().tearDown()
        pathStr = self.manager._configPath()
        del(self.manager)
        rmtree(path.dirname(pathStr))

    def test_load_default_settings(self):
        tpl = config.Settings()

        for key in tpl.__dict__.keys():
            self.assertEqual(getattr(tpl, key), getattr(
                self.manager.settings, key))

    def test_load_with_profile(self):
        profile = config.AWSProfile(label='testProfile', region='test-central-1',
                                    accessKey='accessKey', secretAccessKey='secretAccessKey')

        self.manager.settings.profiles.append(profile)
        self.manager.save()
        self.manager.load()

        self.assertEqual([profile], self.manager.settings.profiles)

    def test_load_with_loadDataOnTabChange(self):
        self.assertFalse(self.manager.settings.loadDataOnTabChange)
        self.manager.settings.loadDataOnTabChange = True

        self.manager.save()
        self.manager.load()

        self.assertTrue(self.manager.settings.loadDataOnTabChange)
