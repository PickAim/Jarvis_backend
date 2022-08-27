import unittest
from ..tests.some_tests_data import cost_data
from ..calc import get_frequency_stats


class FrequencyCalcTest(unittest.TestCase):
    def test_stats_calc(self):
        self.assertEqual(len(get_frequency_stats(cost_data, 100)[0]), 100)

