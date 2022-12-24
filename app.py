import uvicorn
import re
import numpy as np

from jarvis_calc.utils import constants
from jarvis_calc.utils.calc_utils import get_frequency_stats
from jarvis_calc.utils.jarvis_utils import load_data
from jarvis_calc.utils.margin_calc import get_mean_concurrent_cost
from jarvis_calc.utils.margin_calc import unit_economy_calc
from jarvis_calc.utils.load_data import load
from fastapi import FastAPI
from margin_item import MarginItem
from os.path import join
from os.path import abspath


app = FastAPI()


@app.post('/margin/')
def calc_margin(margin_item: MarginItem):
    niche = margin_item.niche.lower()
    niche = re.sub(' +', ' ', niche)
    filename = abspath(str(join(constants.data_path, niche + ".txt")))
    costs = np.array(load_data(filename))
    costs.sort()
    mid_cost = get_mean_concurrent_cost(costs, margin_item.buy,
                        margin_item.pack, 10)  # todo think about number of samples example: int(len(costs) * 0.1)
    result_dict = unit_economy_calc(margin_item.buy, margin_item.pack, mid_cost, margin_item.pack,
                           margin_item.units)
    return result_dict


@app.get('/data/{niche}')
def upload_data(niche: str, is_update: bool = False):
    text_to_search = niche.lower()
    text_to_search = re.sub(' +', ' ', text_to_search)
    load(text_to_search, is_update, 1)  # todo delete 1 after testing
    filename = abspath(
        str(join(constants.data_path, text_to_search + ".txt"))
    )
    cost_data = load_data(filename)
    n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
    x, y = get_frequency_stats(cost_data, n_samples + 1)
    return {'x': x, 'y': y}


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
