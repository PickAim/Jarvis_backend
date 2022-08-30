import numpy as np

# now it's just constants
commission = 0.1
logistic_price = 55
storage_price = 0.04
wrep = 45


def all_calc(buy_price, pack_price, mid_cost, transit_price=0.0, unit_count=0.0) -> dict[str: (float, float)]:
    unit_cost = buy_price + pack_price
    unit_storage_cost = wrep * storage_price

    partial_unit_cost = (unit_cost + logistic_price +
                         unit_storage_cost) * (1 + commission)
    if unit_count > 0:
        partial_unit_transit_cost = partial_unit_cost + \
                                    (transit_price / unit_count) * (1 + commission)
    else:
        partial_unit_transit_cost = 0

    margin = (1 - commission) * mid_cost - partial_unit_cost

    if unit_count > 0:
        transit_margin = (1 - commission) * mid_cost - partial_unit_transit_cost
    else:
        transit_margin = 0

    if margin > 0:
        partial_cost = (unit_cost + logistic_price + margin + unit_storage_cost)
    else:
        partial_cost = (unit_cost + logistic_price + unit_storage_cost)
    cost = (1 + commission) * partial_cost

    if unit_count > 0:
        transit_cost = cost + (transit_price / unit_count) * (1 + commission)
    else:
        transit_cost = 0

    full_commission = commission * partial_cost
    old_margin = margin
    if margin > 0:
        margin = margin * (1 - commission)
    else:
        margin = margin * (1 + commission)
    result = {
        "Pcost": (buy_price, buy_price / (cost - commission * old_margin)),  # Закупочная себестоимость
        "Pack": (pack_price, pack_price / (cost - commission * old_margin)),  # Упаковка
        # Комиссия маркетплейса
        "Mcomm": (full_commission, full_commission / (cost - commission * old_margin)),
        "Log": (logistic_price, logistic_price / (cost - commission * old_margin)),  # Логистика
        "Store": (unit_storage_cost, unit_storage_cost / (cost - commission * old_margin)),  # Хранение
        "Margin": (margin, abs(margin) / (cost - commission * old_margin)),  # Маржа
    }
    if margin > 0:
        result["Price"] = (cost, unit_cost / (cost - commission * old_margin) * 100
                           + full_commission / (cost - commission * old_margin) * 100
                           + logistic_price / (cost - commission * old_margin) * 100
                           + unit_storage_cost / (cost - commission * old_margin) * 100
                           + margin / (cost - commission * old_margin) * 100)  # Цена
    else:
        result["Price"] = (cost, unit_cost / cost * 100
                           + full_commission / cost * 100
                           + logistic_price / cost * 100
                           + unit_storage_cost / cost * 100)  # Цена
    result["Commis"] = cost * commission
    result["tr_margin"] = transit_margin
    result["tr_cost"] = transit_cost
    result["tr_delta"] = transit_cost - cost
    return result


def get_concurrent_margin(mid_cost, unit_cost, unit_storage_cost):
    return (mid_cost - unit_cost - commission * mid_cost - logistic_price - unit_storage_cost) / 0.5


def get_mean(cost_data: np.array, buy_price, pack_price) -> float:
    unit_cost = buy_price + pack_price
    unit_storage_cost = wrep * storage_price
    lower = cost_data[0: len(cost_data) // 3]
    middle = cost_data[len(cost_data) // 3: 2 * len(cost_data) // 3]
    high = cost_data[2 * len(cost_data) // 3:]
    l_concurrent_margin = get_concurrent_margin(
        lower.mean(), unit_cost, unit_storage_cost)
    if buy_price * 100 < l_concurrent_margin:
        return lower.mean() / 100
    m_concurrent_margin = get_concurrent_margin(
        middle.mean(), unit_cost, unit_storage_cost)
    if buy_price * 100 < m_concurrent_margin:
        return middle.mean() / 100
    h_concurrent_margin = get_concurrent_margin(
        high.mean(), unit_cost, unit_storage_cost)
    if buy_price * 100 < h_concurrent_margin:
        return high.mean() / 100
    return cost_data.mean() / 100



