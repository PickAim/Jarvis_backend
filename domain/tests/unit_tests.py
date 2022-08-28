import unittest
import domain.constants as constants
import numpy as np
import json
import time

from os.path import join
from ..tests.some_tests_data import cost_data
from ..calc import get_frequency_stats
from ..load_data import load
from ..jarvis_utils import load_data
from ..margin_calc import get_mean, all_calc


class FrequencyCalcTest(unittest.TestCase):
    def test_stats_calc(self):
        self.assertEqual(len(get_frequency_stats(cost_data, 100)[0]), 100)

    def test_load(self):
        text_to_search = 'молотый кофе'
        is_update = True
        pages_num = 2
        start_time= time.time()
        load(text_to_search, is_update, pages_num)
        print(time.time()-start_time)
        filename = str(join(constants.data_path, text_to_search + ".txt"))
        cost_data = load_data(filename)
        n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
        x, y = get_frequency_stats(cost_data, n_samples + 1)
        self.assertEqual(len(x), n_samples + 1)

    def test_all_calc(self):
        niche = 'молотый кофе'
        filename = str(join(constants.data_path, niche + ".txt"))
        costs = np.array(load_data(filename))
        costs.sort()
        buy = 75
        pack = 25
        transit = 5000
        unit_count = 100

        mid_cost = get_mean(costs, buy, pack)
        result_dict = all_calc(buy, pack, mid_cost, transit,
                               unit_count)
        self.assert_(result_dict)
        with open(join(constants.out_path, 'price.json'), 'w', encoding="UTF-8") as out_json:
            json.dump(result_dict, out_json, indent=4)
