from jarvis_calc.database_interactors.db_controller import DBController
from jorm.market.service import SimpleEconomySaveObject, TransitEconomySaveObject


class RequestHandler:
    def __init__(self, db_controller: DBController):
        self.__db_controller = db_controller

    def save_simple_economy_request(self, save_object: SimpleEconomySaveObject, user_id: int) -> int:
        return self.__db_controller.save_simple_economy_request(save_object, user_id)

    def save_transit_economy_request(self, save_object: TransitEconomySaveObject, user_id: int) -> int:
        return self.__db_controller.save_transit_economy_request(save_object, user_id)

    def get_all_simple_economy_results(self, user_id: int) -> list[SimpleEconomySaveObject]:
        return self.__db_controller.get_all_simple_economy_results(user_id)

    def get_all_transit_economy_results(self, user_id: int) -> list[TransitEconomySaveObject]:
        return self.__db_controller.get_all_transit_economy_results(user_id)

    def delete_simple_economy_request(self, request_id: int, user_id: int) -> None:
        self.__db_controller.delete_simple_economy_request(request_id, user_id)

    def delete_transit_economy_request(self, request_id: int, user_id: int) -> None:
        self.__db_controller.delete_transit_economy_request(request_id, user_id)
