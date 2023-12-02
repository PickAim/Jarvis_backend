from jarvis_factory.factories.jdb import JDBClassesFactory
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.person import User

from jarvis_backend.app.schedule.workers.base import DBWorker
from jarvis_backend.sessions.db_context import DbContext


class UserProductsLoadWorker(DBWorker):
    def __init__(self, db_context: DbContext):
        super().__init__(db_context)

    @classmethod
    def get_identifier(cls) -> str:
        return "user_products_load"

    def load_users_products(self) -> None:
        users: list[User] = self.__get_all_users()
        user_id_to_marketplace_ids = self.__map_users_to_added_marketplaces(users)
        for user_id in user_id_to_marketplace_ids:
            marketplace_ids = user_id_to_marketplace_ids[user_id]
            for marketplace_id in marketplace_ids:
                self.__load_user_products(user_id, marketplace_id)

    def __get_all_users(self) -> list[User]:
        with self._db_context.session() as session, session.begin():
            user_service = JDBServiceFactory.create_user_service(session)
            return list(user_service.find_all().values())

    @staticmethod
    def __map_users_to_added_marketplaces(users: list[User]) -> dict[int, list[int]]:
        return {
            user.user_id: user.marketplace_keys.keys() for user in users
        }
    
    def __load_user_products(self, user_id: int, marketplace_id: int) -> None:
        with self._db_context.session() as session, session.begin():
            jorm_changer = JDBClassesFactory.create_jorm_changer(session, marketplace_id=marketplace_id,
                                                                 user_id=user_id)
            jorm_changer.load_user_products(user_id=user_id, marketplace_id=marketplace_id)
