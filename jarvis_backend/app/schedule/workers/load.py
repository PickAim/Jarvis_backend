import logging
from time import time

from jarvis_db.access.fill.support.constants import NICHE_TO_CATEGORY, WILDBERRIES_NAME
from jarvis_factory.factories.jdb import JDBClassesFactory
from jarvis_factory.support.jdb.services import JDBServiceFactory

from jarvis_backend.app.constants import COMMISSIONS_FILE
from jarvis_backend.app.loggers import BACKGROUND_LOGGER, ERROR_LOGGER
from jarvis_backend.app.schedule.workers.base import DBWorker
from jarvis_backend.sessions.db_context import DbContext

_LOGGER = logging.getLogger(BACKGROUND_LOGGER + ".load")


class LoadWorker(DBWorker):
    def __init__(self, db_context: DbContext, load_skip: int):
        super().__init__(db_context)
        self.__load_skip = load_skip

    @classmethod
    def get_identifier(cls) -> str:
        return 'load_niche'

    def load_niches(self):
        lines = self.__get_file_lines()
        wb_id = self._get_wb_id()
        if wb_id == -1:
            return
        for i in range(0, len(lines), self.__load_skip):
            if not self.is_alive():
                return
            splitted: list[str] = lines[i].split(";")
            niche_name = splitted[1]
            if self.__should_skip_niche(niche_name, wb_id, NICHE_TO_CATEGORY):
                _LOGGER.info(f"Niche \"{niche_name}\" skipped.")
                continue
            self.__try_to_load_niche(niche_name, wb_id)  # todo for now it only WB

    def _get_wb_id(self) -> int:
        with self._db_context.session() as session, session.begin():
            marketplace_service = JDBServiceFactory.create_marketplace_service(session)
            found = marketplace_service.find_by_name(WILDBERRIES_NAME)
            if found is not None:
                return found[1]
            return -1

    @staticmethod
    def __get_file_lines() -> list[str]:
        with open(COMMISSIONS_FILE, "r", encoding='cp1251') as file:
            return file.readlines()

    def __try_to_load_niche(self, niche_name: str, marketplace_id: int):
        with self._db_context.session() as session, session.begin():
            jorm_changer = JDBClassesFactory.create_jorm_changer(session, marketplace_id=marketplace_id, user_id=0)
            try:
                _LOGGER.info(f"Start loading Niche \"{niche_name}\".")
                start = time()
                niche = jorm_changer.load_new_niche(niche_name, marketplace_id)
                if niche is None:
                    raise Exception("niche is None")
                _LOGGER.info(f"Niche \"{niche_name}\" loaded with {len(niche.products)} products - {time() - start}s.")
            except Exception:
                error_logger = logging.getLogger(ERROR_LOGGER)
                error_logger.exception(f"Niche \"{niche_name}\"not loaded, cause:\n", stacklevel=5, exc_info=True)

    def __should_skip_niche(self, niche_name: str, marketplace_id: int, niche_to_category: dict[str, str]):
        if niche_name not in niche_to_category:
            return False
        category_name = niche_to_category[niche_name]
        with self._db_context.session() as session, session.begin():
            category_service = JDBServiceFactory.create_category_service(session)
            found = category_service.find_by_name(category_name, marketplace_id=marketplace_id)
            if found is None:
                return False
            _, category_id = found
            niche_service = JDBServiceFactory.create_niche_service(session)
            found = niche_service.find_by_name(niche_name, category_id)
            return found is not None
