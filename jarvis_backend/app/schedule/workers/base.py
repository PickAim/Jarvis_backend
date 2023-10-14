import re

from jarvis_factory.support.jdb.services import JDBServiceFactory

from jarvis_backend.sessions.db_context import DbContext


class DBWorker:
    def __init__(self, db_context: DbContext):
        self._db_context = db_context

    @staticmethod
    def __is_default_object(object_name: str) -> bool:
        return re.search('default', object_name, re.IGNORECASE) is not None

    def _get_all_niche_ids(self):
        niche_ids = []
        marketplace_ids = self._get_marketplace_ids()
        for marketplace_id in marketplace_ids:
            category_ids = self._get_category_ids(marketplace_id)
            for category_id in category_ids:
                niche_ids.extend(self._get_niche_ids(category_id))
        return niche_ids

    def _get_marketplace_ids(self) -> list[int]:
        with self._db_context.session() as session, session.begin():
            marketplace_service = JDBServiceFactory.create_marketplace_service(session)
            all_marketplaces = marketplace_service.find_all()
            return [marketplace_id
                    for marketplace_id in all_marketplaces
                    if not self.__is_default_object(all_marketplaces[marketplace_id].name)]

    def _get_category_ids(self, marketplace_id: int) -> list[int]:
        with self._db_context.session() as session, session.begin():
            category_service = JDBServiceFactory.create_category_service(session)
            return [category_id for category_id in category_service.find_all_in_marketplace(marketplace_id)]

    def _get_niche_ids(self, category_id: int) -> list[int]:
        with self._db_context.session() as session, session.begin():
            niche_service = JDBServiceFactory.create_niche_service(session)
            return list(niche_service.find_all_in_category(category_id).keys())
