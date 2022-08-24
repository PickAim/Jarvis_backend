
#ввод пользоателя
buy_price = 41
pack_price = 4.4
weight = 0.250  # ????
# это берем с ВБ
commission = 0.1
logistic_price = 55
storage_price = 0.04
wrep = 45
# ввод по транзиту
unit_count = 216
transit_price = 5000
#внешние показатели
mid_cost = 1613

unit_cost = buy_price + pack_price
unit_storage_cost = wrep * storage_price

partial_unit_cost = (unit_cost + logistic_price + unit_storage_cost) * (1 + commission)
partial_unit_transit_cost = partial_unit_cost + (transit_price / unit_count) * (1 + commission)

margin = (1 - commission) * mid_cost - partial_unit_cost
concurrent_margin = (mid_cost - unit_cost - pack_price - commission * mid_cost - logistic_price - unit_storage_cost)/0.5
margin = margin * buy_price / concurrent_margin
transit_margin = (1 - commission) * mid_cost - partial_unit_transit_cost

cost = (1 + commission) * (unit_cost + logistic_price + margin + unit_storage_cost)
transit_cost = cost + (transit_price / unit_count) * (1 + commission)

full_commission = commission * (unit_cost + logistic_price + margin + unit_storage_cost)

print(margin / cost * 100)  # расчет процента маржи, пункт 4 из экселя
print("Параметры для диаграмки: ")
print("Закупочная себестоимость:", unit_cost, unit_cost/cost * 100)
print("Упаковка:                ", pack_price, pack_price/cost * 100)
print("комиссия маркетплейс:    ", full_commission, full_commission/cost * 100)
print("Логистика:               ", logistic_price, logistic_price/cost * 100)
print("Хранение:                ", unit_storage_cost, unit_storage_cost/cost * 100)
print("Маржа:                   ", margin, margin/cost * 100)
print("Цена:                    ", cost, unit_cost/cost * 100 + full_commission/cost * 100 + logistic_price/cost * 100 +
      unit_storage_cost/cost * 100 + margin/cost * 100)

