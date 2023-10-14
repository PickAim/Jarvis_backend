import logging
from time import time

from jarvis_db.access.fill.support.constatns import WILDBERRIES_NAME
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

    def load_niches(self):
        lines = self.__get_file_lines()
        wb_id = self._get_wb_id()
        if wb_id == -1:
            return
        for i in range(0, len(lines), self.__load_skip):
            splitted: list[str] = lines[i].split(";")
            niche_name = splitted[1]
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
                start = time()
                niche = jorm_changer.load_new_niche(niche_name, marketplace_id)
                _LOGGER.info(f"Niche \"{niche_name}\" loaded with {len(niche.products)} products - {time() - start}s.")
            except Exception as ex:
                error_logger = logging.getLogger(ERROR_LOGGER)
                error_logger.error(f"Niche \"{niche_name}\"not loaded, cause:\n{str(ex)}")
