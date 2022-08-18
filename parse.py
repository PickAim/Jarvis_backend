import numpy as np
import matplotlib.pyplot as plt

from tests.some_tests_data import data


def get_percent_that_higher(cost_data: list[float], cost):
    cost_data = cost_data.copy()
    cost_data.sort()


def frequency_calc2(costs: np.array, n_samples: int):
    keys = []
    frequency = []
    maximum = costs.max()
    minimum = costs.min()
    step = (maximum - minimum) // n_samples
    for i in range(n_samples):
        keys.append((i + 1) * step + minimum)
        frequency.append(0)
    print(len(keys))
    i = 0
    for cost in costs:
        while cost > keys[i]:
            i += 1
            if i >= n_samples - 1:
                i -= 1
                break
        frequency[i] += 1
    return keys, frequency


def get_frequency_stats(cost_data: list[float], n_samples: int):
    cost_data.sort()
    cost_data = np.array(cost_data)
    keys, frequency = frequency_calc2(cost_data, n_samples)
    plt.plot(keys, frequency)
    plt.grid(True)
    plt.show()
    math_ozh = 0
    clear_frequency = np.array([x for x in frequency if x != 0])
    for freq in clear_frequency:
        math_ozh += freq/len(clear_frequency)
    math_ozh = int(math_ozh)  # binary search of math mean
    interesting_part_ind = 0
    while frequency[interesting_part_ind] > math_ozh:
        interesting_part_ind += 1
    if interesting_part_ind > 0:
        right_key = keys[interesting_part_ind]
        sum = 0
        for i in range(interesting_part_ind, len(frequency)):
            sum += frequency[i]
        right_frequency = sum
        left_costs = []
        for cost in cost_data:
            if cost < keys[interesting_part_ind - 1]:
                left_costs.append(cost)
            else:
                break
        keys, frequency = frequency_calc2(np.array(left_costs), n_samples - 1)
        keys.append(right_key)
        frequency.append(right_frequency)
    plt.plot(keys, frequency)
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    # get_stats(data)
    get_frequency_stats(data, 10)
    # getAllPdoructNiche("кофе зерновой")




