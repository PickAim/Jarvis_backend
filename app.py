import uvicorn
import re
import numpy as np

from logic import constants
from logic.margin_calc import load_data
from logic.margin_calc import get_mean
from logic.margin_calc import all_calc
from logic.load_data import get_all_product_niche
from logic.calc import get_frequency_stats
from fastapi import FastAPI
from margin_item import MarginItem
from os import listdir
from os.path import join
from os.path import isfile
from os.path import exists
from os.path import abspath
from os import mkdir


app = FastAPI()


@app.post('/margin/')
async def calc_margin(margin_item: MarginItem):
    niche = margin_item.niche.lower()
    niche = re.sub(' +', ' ', niche)
    filename = abspath(str(join(constants.data_path, niche + ".txt")))
    costs = np.array(load_data(filename))
    costs.sort()
    mid_cost = get_mean(costs, margin_item.buy, margin_item.pack)
    result_dict = all_calc(margin_item.buy, margin_item.pack, mid_cost, margin_item.pack,
                           margin_item.units)
    return result_dict


@app.get('/data/{niche}')  # todo add parameter (is_update) in request
async def upload_data(niche: str, is_update: bool):
    text_to_search = niche.lower()
    text_to_search = re.sub(' +', ' ', text_to_search)
    only_files = []
    if exists(constants.data_path):
        only_files = [f.split('.')[0] for f in listdir(
            constants.data_path) if isfile(join(constants.data_path, f))]
    else:
        mkdir(constants.data_path)
    if not text_to_search in only_files or is_update:
        get_all_product_niche(text_to_search, abspath(constants.data_path))
    filename = abspath(
        str(join(constants.data_path, text_to_search + ".txt"))
    )
    cost_data = load_data(filename)
    n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
    x, y = get_frequency_stats(cost_data, n_samples + 1)
    return {'x': x, 'y': y}


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
