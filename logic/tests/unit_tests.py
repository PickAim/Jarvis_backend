import unittest
import logic.constants as constants

from os.path import join
from ..tests.some_tests_data import cost_data
from ..calc import get_frequency_stats
from ..load_data import load
from ..jarvis_utils import load_data


class FrequencyCalcTest(unittest.TestCase):
    def test_stats_calc(self):
        self.assertEqual(len(get_frequency_stats(cost_data, 100)[0]), 100)

    def test_load(self):
        text_to_search = 'молотый кофе'
        is_update = False
        load(text_to_search, is_update)
        filename = str(join(constants.data_path, text_to_search + ".txt"))
        cost_data = load_data(filename)
        n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
        x, y = get_frequency_stats(cost_data, n_samples + 1)
        self.assertEqual(len(x), n_samples + 1)
