import uvicorn
import re
import numpy as np

from fastapi import FastAPI

from os.path import join
from os.path import abspath, dirname

from jarvis_calc.utils.calc_utils import get_frequency_stats
from jarvis_calc.factories import JORMFactory
from jarvis_calc.utils.margin_calc import unit_economy_calc, unit_economy_calc_with_jorm

from jorm.market.infrastructure import Niche, Warehouse

from jdu.request.loader_utils import load_cost_data_from_file, load_niche_info

from margin_item import MarginItem, MarginJormItem


app = FastAPI()

storage_dir = join(dirname(__file__), "data")

jorm_factory: JORMFactory = JORMFactory()  # TODO move to login or session creating request


@app.post('/margin/')
def calc_margin(margin_item: MarginItem):
    niche = margin_item.niche.lower()
    niche = re.sub(' +', ' ', niche)
    load_niche_info(niche, storage_dir, pages_num=1)
    filename = abspath(str(join(storage_dir, niche + ".txt")))
    costs = np.array(load_cost_data_from_file(filename))
    costs.sort()
    result_dict = unit_economy_calc(margin_item.buy, margin_item.pack, margin_item.commission,
                                    margin_item.logistic_to_customer, margin_item.storage_price,
                                    margin_item.returned_percent, margin_item.client_tax, costs,
                                    margin_item.transit_price, margin_item.transit_count)
    return result_dict


@app.post('/jorm_margin/')
def calc_margin(margin_item: MarginJormItem):
    niche: Niche = jorm_factory.niche(margin_item.niche)
    warehouse: Warehouse = jorm_factory.warehouse(margin_item.warehouse_name)
    result_dict = unit_economy_calc_with_jorm(margin_item.buy, margin_item.pack, niche,
                                              warehouse, jorm_factory.get_current_client())
    return result_dict


@app.get('/data/{niche}')
def upload_data(niche: str, is_update: bool = False):
    text_to_search = niche.lower()
    text_to_search = re.sub(' +', ' ', text_to_search)
    load_niche_info(niche, storage_dir, is_update, pages_num=1)
    filename = abspath(
        str(join(storage_dir, text_to_search + ".txt"))
    )
    cost_data = load_cost_data_from_file(filename)
    n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
    x, y = get_frequency_stats(cost_data, n_samples + 1)
    return {'x': x, 'y': y}


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
