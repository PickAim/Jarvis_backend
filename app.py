import uvicorn

from fastapi import FastAPI

from jarvis_calc.database_interactors.db_access import DBUpdateProvider
from jarvis_calc.utils.calc_utils import get_frequency_stats_with_jorm
from jarvis_calc.factories import JORMFactory
from jarvis_calc.utils.margin_calc import unit_economy_calc_with_jorm

from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.service import Request

from margin_item import MarginJormItem


app = FastAPI()

jorm_factory: JORMFactory = JORMFactory()  # TODO move to login or session creating request

db_updater: DBUpdateProvider  # TODO move to login or session creating request


@app.post('/jorm_margin/')
def calc_margin(margin_item: MarginJormItem):
    niche: Niche = jorm_factory.niche(margin_item.niche)
    warehouse: Warehouse = jorm_factory.warehouse(margin_item.warehouse_name)
    result_dict = unit_economy_calc_with_jorm(margin_item.buy, margin_item.pack, niche,
                                              warehouse, jorm_factory.get_current_client(), margin_item.transit_price,
                                              margin_item.transit_count, margin_item.transit_price)
    return result_dict


@app.get('/jorm_data/{niche}')
def upload_data(niche: str):
    niche: Niche = jorm_factory.niche(niche)
    x, y = get_frequency_stats_with_jorm(niche)
    return {'x': x, 'y': y}


@app.get('/save_request/{request}')
def upload_data(request_json: str):
    request_to_save: Request = jorm_factory.request(request_json)
    db_updater.save_request(request_to_save)


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
