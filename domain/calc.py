import numpy as np
import matplotlib.pyplot as plt


def frequency_calc(costs: np.array, n_samples: int):
    res = plt.hist(costs, n_samples)
    plt.clf()
    return list(res[1][1:]), list(res[0])


def get_mean(lst: list[int]) -> int:
    result = 0
    clear_frequency = np.array([x for x in lst if x != 0])
    for freq in clear_frequency:
        result += freq / len(clear_frequency)
    return int(result)


def get_frequency_stats(cost_data: list[float], n_samples: int) -> tuple[list[float], list[float]]:
    if len(cost_data) <= 0:
        return [], []
    cost_data.sort()
    cost_data = np.array(cost_data)
    base_keys, base_frequency = frequency_calc(cost_data, n_samples)
    keys = base_keys.copy()
    frequency = base_frequency.copy()
    # plt.plot(keys, frequency)  # just show graphics
    # plt.grid(True)
    # plt.show()
    math_ozh = get_mean(frequency)
    interesting_part_ind = len(keys)//3
    if len(frequency) < 2:
        return keys, frequency
    while frequency[interesting_part_ind] > math_ozh//2 and interesting_part_ind < len(frequency):  # todo
        interesting_part_ind += 1
    while True:
        if 0 < interesting_part_ind < len(frequency):
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
            keys, frequency = frequency_calc(
                np.array(left_costs), n_samples - 1)
            keys.append(right_key)
            frequency.append(right_frequency)
            if right_frequency > get_mean(frequency):
                interesting_part_ind += 1
                frequency = base_frequency
                keys = base_keys
            else:
                break
        else:
            break
    # plt.plot(keys, frequency)  # just show graphics
    # plt.grid(True)
    # plt.show()
    return keys, frequency
