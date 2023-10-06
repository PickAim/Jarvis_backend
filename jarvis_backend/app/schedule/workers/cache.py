import logging
import re
from datetime import datetime
from time import time

from jarvis_factory.support.jdb.services import JDBServiceFactory

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.loggers import BACKGROUND_LOGGER
from jarvis_backend.sessions.db_context import DbContext

_LOGGER = logging.getLogger(BACKGROUND_LOGGER + ".cache")


class CacheWorker:
    def __init__(self, db_context: DbContext):
        self.__db_context = db_context

    def update_all_caches(self):
        with self.__db_context.session() as session, session.begin():
            marketplace_service = JDBServiceFactory.create_marketplace_service(session)
            all_marketplaces = marketplace_service.find_all()
            marketplace_ids = [marketplace_id
                               for marketplace_id in all_marketplaces
                               if not self.__is_default_object(all_marketplaces[marketplace_id].name)]
        for marketplace_id in marketplace_ids:
            self.__update_cache_for(marketplace_id)

    @staticmethod
    def __is_default_object(object_name: str) -> bool:
        return re.search('default', object_name, re.IGNORECASE) is not None

    def __update_cache_for(self, marketplace_id: int):
        category_ids = self.__get_category_ids(marketplace_id)
        niche_ids = self.__get_niche_ids(category_ids)
        self.__update_niche_calculation_cache(niche_ids)

    def __get_category_ids(self, marketplace_id: int) -> list[int]:
        with self.__db_context.session() as session, session.begin():
            category_service = JDBServiceFactory.create_category_service(session)
            return [category_id for category_id in category_service.find_all_in_marketplace(marketplace_id)]

    def __get_niche_ids(self, category_ids: list[int]) -> list[int]:
        niche_ids: list[int] = []
        with self.__db_context.session() as session, session.begin():
            niche_service = JDBServiceFactory.create_niche_service(session)
            for category_id in category_ids:
                niche_ids.extend(list(niche_service.find_all_in_category(category_id).keys()))
        return niche_ids

    def __update_niche_calculation_cache(self, niche_ids: list[int]):
        for niche_id in niche_ids:
            with self.__db_context.session() as session, session.begin():
                niche_service = JDBServiceFactory.create_niche_service(session)
                start = time()
                niche = niche_service.fetch_by_id_atomic(niche_id)
                _LOGGER.info(f'Niche#{niche_id} {niche.name} loaded - {time() - start}s')
                niche_characteristics_service = JDBServiceFactory.create_niche_characteristics_service(session)
                start = time()
                characteristics = CalculationController.calc_niche_characteristics(niche)
                niche_characteristics_service.upsert(niche_id, characteristics)
                CalculationController.calc_green_zone(niche, datetime.utcnow())
                _LOGGER.info(f'Niche#{niche_id} {niche.name} cached - {time() - start}s')
