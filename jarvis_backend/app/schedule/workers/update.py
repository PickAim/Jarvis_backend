import logging
from time import time

from jarvis_factory.factories.jdb import JDBClassesFactory
from jarvis_factory.support.jdb.services import JDBServiceFactory

from jarvis_backend.app.loggers import BACKGROUND_LOGGER, ERROR_LOGGER
from jarvis_backend.app.schedule.workers.base import DBWorker
from jarvis_backend.sessions.db_context import DbContext

_LOGGER = logging.getLogger(BACKGROUND_LOGGER + ".update")


class UpdateWorker(DBWorker):
    def __init__(self, db_context: DbContext):
        super().__init__(db_context)

    @classmethod
    def get_identifier(cls) -> str:
        return 'update_niche'

    def update_niches(self):
        marketplace_category_niche_ids: dict[int, dict[int, list[int]]] = self.__get_mapped_ids()
        for marketplace_id in marketplace_category_niche_ids:
            category_to_niche_ids = marketplace_category_niche_ids[marketplace_id]
            self.__update_categories(category_to_niche_ids, marketplace_id)

    def __update_categories(self, category_to_niche_ids: dict[int, list[int]], marketplace_id: int):
        for category_id in category_to_niche_ids:
            if not self.is_alive():
                return
            niche_ids = category_to_niche_ids[category_id]
            self.__update_niches(niche_ids, category_id, marketplace_id)

    def __update_niches(self, niche_ids: list[int], category_id: int, marketplace_id: int):
        for niche_id in niche_ids:
            if not self.is_alive():
                return
            self.__update_niche(niche_id, category_id, marketplace_id)

    def __update_niche(self, niche_id: int, category_id: int, marketplace_id: int):
        with self._db_context.session() as session, session.begin():
            niche_service = JDBServiceFactory.create_niche_service(session)
            niche = niche_service.find_by_id(niche_id)
            if self._is_default_object(niche.name):
                return
            jorm_changer = JDBClassesFactory.create_jorm_changer(session, marketplace_id, 0)
            try:
                start = time()
                niche = jorm_changer.update_niche(niche_id, category_id, marketplace_id)
                _LOGGER.info(f"Niche#{niche_id} \"{niche.name}\" updated - {time() - start}s.")
            except Exception:
                error_logger = logging.getLogger(ERROR_LOGGER)
                error_logger.exception(f"Niche#{niche_id} \"{niche.name}\" not updated, cause:\n",
                                       stacklevel=5, exc_info=True)

    def __get_mapped_ids(self) -> dict[int, dict[int, list[int]]]:
        marketplace_category_niche_ids: dict[int, dict[int, list[int]]] = {}
        marketplace_ids = self._get_marketplace_ids()
        for marketplace_id in marketplace_ids:
            if marketplace_id not in marketplace_category_niche_ids:
                marketplace_category_niche_ids[marketplace_id] = {}
            category_ids = self._get_category_ids(marketplace_id)
            for category_id in category_ids:
                marketplace_category_niche_ids[marketplace_id][category_id] = self._get_niche_ids(category_id)
        return marketplace_category_niche_ids
