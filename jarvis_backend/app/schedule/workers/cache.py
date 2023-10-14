import logging
from datetime import datetime
from time import time

from jarvis_factory.support.jdb.services import JDBServiceFactory

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.loggers import BACKGROUND_LOGGER
from jarvis_backend.app.schedule.workers.base import DBWorker
from jarvis_backend.sessions.db_context import DbContext

_LOGGER = logging.getLogger(BACKGROUND_LOGGER + ".cache")


class CacheWorker(DBWorker):
    def __init__(self, db_context: DbContext):
        super().__init__(db_context)

    def update_all_caches(self):
        niche_ids = self._get_all_niche_ids()
        self.__update_niche_calculation_cache(niche_ids)

    def __update_niche_calculation_cache(self, niche_ids: list[int]):
        for niche_id in niche_ids:
            with self._db_context.session() as session, session.begin():
                niche_service = JDBServiceFactory.create_niche_service(session)
                niche_characteristics_service = JDBServiceFactory.create_niche_characteristics_service(session)
                green_trade_zone_service = JDBServiceFactory.create_green_trade_zone_service(session)
                start = time()
                niche = niche_service.fetch_by_id_atomic(niche_id)
                _LOGGER.info(f'Niche#{niche_id} {niche.name} loaded - {time() - start}s.')
                start = time()
                niche_characteristics = CalculationController.calc_niche_characteristics(niche)
                niche_characteristics_service.upsert(niche_id, niche_characteristics)
                niche_green_trade_zone = CalculationController.calc_green_zone(niche, datetime.utcnow())
                green_trade_zone_service.upsert(niche_id, niche_green_trade_zone)
                _LOGGER.info(f'Niche#{niche_id} {niche.name} cached - {time() - start}s.')
