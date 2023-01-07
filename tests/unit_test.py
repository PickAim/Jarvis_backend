import time
import unittest
from os.path import join

from jdu.request.loader_utils import load_niche_info, load_cost_data_from_file

import app


class FrequencyCalcTest(unittest.TestCase):
    def test_calc_compatibility(self):
        text_to_search = 'молотый кофе'
        is_update = True
        pages_num = 1
        start_time = time.time()
        load_niche_info(text_to_search, app.storage_dir, is_update, pages_num)
        print(time.time() - start_time)
        filename = str(join(app.storage_dir, text_to_search + ".txt"))
        cost_data = load_cost_data_from_file(filename)
        self.assertIsNotNone(cost_data)
        self.assertNotEqual(0, len(cost_data))
