import unittest
import domain.constants as constants
import numpy as np
import time

from os.path import join

import domain.load_data
from some_tests_data import cost_data
from domain.calc import get_frequency_stats
from domain.load_data import load
from domain.load_storage import get_storage_data
from domain.jarvis_utils import load_data
from domain.margin_calc import get_mean, all_calc


class FrequencyCalcTest(unittest.TestCase):
    def test_stats_calc(self):
        self.assertEqual(len(get_frequency_stats(cost_data, 100)[0]), 100)

    def test_all_calc(self):
        niche = 'кофе'
        is_update = False
        pages_num = 1
        load(niche, is_update, pages_num)
        filename = str(join(constants.data_path, niche + ".txt"))
        costs = np.array(load_data(filename))
        costs.sort()
        buy = 500
        pack = 150
        transit = 0
        unit_count = 0
        mid_cost = get_mean(costs, buy, pack, 20)
        result_dict = all_calc(buy, pack, mid_cost, transit,
                               unit_count)
        self.assertTrue(result_dict)

    def test_load(self):
        text_to_search = 'молотый кофе'
        is_update = True
        pages_num = 1
        start_time = time.time()
        load(text_to_search, is_update, pages_num)
        print(time.time()-start_time)
        filename = str(join(constants.data_path, text_to_search + ".txt"))
        cost_data = load_data(filename)
        n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
        x, y = get_frequency_stats(cost_data, n_samples + 1)
        self.assertEqual(len(x), n_samples + 1)


    def test_hoba(self):
        arr = np.array([a for a in range(1, 16)])
        print(arr)
        print(arr * np.array([arr]).swapaxes(0, 1))


    def test_load_storage(self):
        text = ['26414401', '6170053']
        print(get_storage_data(text))

