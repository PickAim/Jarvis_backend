import unittest

from jarvis_calc.utils.calc_utils import get_cleared_mean


class FrequencyCalcTest(unittest.TestCase):
    def test_calc_compatibility(self):
        val = get_cleared_mean([1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(5, val)


if __name__ == '__main__':
    unittest.main()
