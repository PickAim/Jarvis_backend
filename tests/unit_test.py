import time
import unittest
from os.path import join

from jarvis_calc import constants
from jarvis_calc.jarvis_utils import load_data
from jarvis_calc.load_data import load


class FrequencyCalcTest(unittest.TestCase):
    def test_calc_compatibility(self):
        text_to_search = 'молотый кофе'
        is_update = True
        pages_num = 1
        start_time = time.time()
        load(text_to_search, is_update, pages_num)
        print(time.time() - start_time)
        filename = str(join(constants.data_path, text_to_search + ".txt"))
        cost_data = load_data(filename)
        self.assertIsNotNone(cost_data)
        self.assertNotEqual(0, len(cost_data))

