from unittest import TestCase

from lib import listUtils


class ListUtilsTestCase(TestCase):
    def test_popValues_scalar_values(self):
        myList = [1, 2, 'a', 'b']
        self.assertTrue(listUtils.popValues(myList, 1, 'a', 'zzz'))
        self.assertEqual([2, 'b'], myList)

    def test_popValues_object_values(self):
        obj = {'a': 1, 'b': 2}
        myList = [1, 2, 'a', obj]
        self.assertTrue(listUtils.popValues(myList, obj))
        self.assertEqual([1, 2, 'a'], myList)

    def test_popValues_value_not_found(self):
        myList = [1, 2, 3, 4]
        self.assertFalse(listUtils.popValues(myList, 5, 6, 7))
        self.assertEqual(myList, [1, 2, 3, 4])
