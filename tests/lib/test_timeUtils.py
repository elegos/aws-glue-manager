from unittest import TestCase
from lib import timeUtils


class TimeUtilTestCase(TestCase):
    def test_fromTimeToString(self):
        self.assertEqual('01:00:00', timeUtils.fromTimeToString(0, 0, 3600))
        self.assertEqual('01:00:00', timeUtils.fromTimeToString(0, 60, 0))
        self.assertEqual('01:00:00', timeUtils.fromTimeToString(1, 0, 0))

        self.assertEqual('01:00:01', timeUtils.fromTimeToString(0, 0, 3601))
        self.assertEqual('01:01:11', timeUtils.fromTimeToString(0, 0, 3671))
        self.assertEqual('01:00:15', timeUtils.fromTimeToString(0, 60, 15))
        self.assertEqual('01:23:57', timeUtils.fromTimeToString(1, 23, 57))
