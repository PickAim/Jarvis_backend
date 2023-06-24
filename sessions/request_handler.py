from typing import TypeVar, Type, Callable

from jarvis_calc.database_interactors.db_controller import DBController
from jarvis_factory.factories.jorm import JORMClassesFactory
from jorm.market.service import UnitEconomyRequest, FrequencyRequest, RequestInfo, \
    Request, Result, UnitEconomyResult, FrequencyResult

from support.types import JBasicSaveObject, JEconomySaveObject, JFrequencySaveObject


def __save_unit_economy_request(db_controller: DBController, save_object: JEconomySaveObject,
                                user_id: int) -> int:
    request = save_object.request
    result = save_object.result
    info = save_object.info
    try:
        return db_controller.save_unit_economy_request(request, result, info, user_id)
    except Exception:
        print("SAVED TO DEFAULT NICHE")
        request.niche = JORMClassesFactory.create_default_niche().name
        request.category = JORMClassesFactory.create_default_category().name
        request.warehouse_name = JORMClassesFactory.create_simple_default_warehouse().name
        return db_controller.save_unit_economy_request(request, result, info, user_id)


def __save_frequency_request(db_controller: DBController, save_object: JFrequencySaveObject, user_id: int):
    request = save_object.request
    result = save_object.result
    info = save_object.info
    return db_controller.save_frequency_request(request, result, info, user_id)


SAVE_METHODS: dict[Type[JBasicSaveObject],
                   Callable[
                       [
                           DBController,
                           JBasicSaveObject | JEconomySaveObject | JFrequencySaveObject,
                           int
                       ],
                       int]] = {
    JEconomySaveObject: __save_unit_economy_request,
    JFrequencySaveObject: __save_frequency_request
}


def __get_all_unit_economy_results(db_controller: DBController, user_id: int) \
        -> list[tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]:
    return db_controller.get_all_unit_economy_results(user_id)


def __get_all_frequency_results(db_controller: DBController, user_id: int) \
        -> list[tuple[FrequencyRequest, FrequencyResult, RequestInfo]]:
    return db_controller.get_all_frequency_results(user_id)


GET_ALL_METHODS: dict[Type[JBasicSaveObject],
                      Callable[
                          [
                              DBController,
                              int
                          ],
                          list[
                              tuple[Request, Result, RequestInfo]
                          ]
                      ]] = {
    JEconomySaveObject: __get_all_unit_economy_results,
    JFrequencySaveObject: __get_all_frequency_results
}


def __delete_unit_economy_request(db_controller: DBController, request_id: int, user_id: int):
    db_controller.delete_unit_economy_request_for_user(request_id, user_id)


def __delete_frequency_request(db_controller: DBController, request_id: int, user_id: int):
    db_controller.delete_frequency_request_for_user(request_id, user_id)


DELETE_METHODS: dict[Type[JBasicSaveObject],
                     Callable[
                         [
                             DBController,
                             int,
                             int
                         ],
                         None
                     ]] = {
    JEconomySaveObject: __delete_unit_economy_request,
    JFrequencySaveObject: __delete_frequency_request
}

T = TypeVar('T')


class RequestHandler:
    def __init__(self, db_controller: DBController,
                 save_methods: dict[Type[JBasicSaveObject],
                                    Callable[
                                        [
                                            DBController,
                                            JBasicSaveObject | JEconomySaveObject | JFrequencySaveObject,
                                            int
                                        ],
                                        int]],
                 get_all_methods: dict[Type[JBasicSaveObject],
                                       Callable[
                                           [
                                               DBController,
                                               int
                                           ],
                                           list[
                                               tuple[Request, Result, RequestInfo]
                                           ]
                                       ]],
                 delete_methods: dict[Type[JBasicSaveObject],
                                      Callable[
                                          [
                                              DBController,
                                              int,
                                              int
                                          ],
                                          None
                                      ]]
                 ):
        self.__db_controller = db_controller
        self.__SAVE_METHODS = save_methods
        self.__GET_ALL_METHODS = get_all_methods
        self.__DELETE_METHODS = delete_methods

    @staticmethod
    def __get_executed_method(mapped_type, methods_map: dict[Type[JBasicSaveObject], T]) -> T:
        if mapped_type not in methods_map:
            raise Exception(str(type(RequestHandler)) + ": unexpected request type")
        return methods_map[mapped_type]

    def save_request(self, user_id: int, save_object: JBasicSaveObject) -> int:
        save_method = self.__get_executed_method(type(save_object), self.__SAVE_METHODS)
        return save_method(self.__db_controller, save_object, user_id)

    def get_all_request_results(self, user_id: int, request_type: T) -> list[tuple[Request, Result, RequestInfo]]:
        get_all_method = self.__get_executed_method(request_type, self.__GET_ALL_METHODS)
        return get_all_method(self.__db_controller, user_id)

    def delete_request(self, request_id: int, user_id: int, request_type: T) -> None:
        delete_method = self.__get_executed_method(request_type, self.__DELETE_METHODS)
        delete_method(self.__db_controller, request_id, user_id)
