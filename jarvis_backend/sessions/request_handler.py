from typing import TypeVar, Type, Callable

from jarvis_calc.database_interactors.db_controller import DBController
from jorm.market.service import UnitEconomyRequest, RequestInfo, \
    Request, Result, UnitEconomyResult
from jorm.support.constants import DEFAULT_CATEGORY_NAME

from jarvis_backend.support.types import JBasicSaveObject, JEconomySaveObject


def __get_default_category_id(db_controller: DBController, marketplace_id: int) -> int:
    id_to_category = db_controller.get_all_categories(marketplace_id)
    for category_id in id_to_category:
        if id_to_category[category_id].name == DEFAULT_CATEGORY_NAME:
            return category_id
    return -1


def __save_unit_economy_request(db_controller: DBController,
                                save_object: JEconomySaveObject,
                                user_id: int, is_save_to_default: bool = False) -> int:
    request = save_object.request
    result = save_object.result
    info = save_object.info
    if not isinstance(request, UnitEconomyRequest) or not isinstance(result, UnitEconomyResult):
        raise Exception(str(type(RequestHandler)) + " - unexpected request or result type")
    request.niche = request.niche.lower()
    if is_save_to_default:
        request.category_id = __get_default_category_id(db_controller, request.marketplace_id)
    return db_controller.save_unit_economy_request(request, result, info, user_id)


SAVE_METHODS: dict[Type[JBasicSaveObject],
Callable[
    [
        DBController,
        JBasicSaveObject | JEconomySaveObject,
        int, bool
    ],
    int]] = {
    JEconomySaveObject: __save_unit_economy_request,
}


def __get_all_unit_economy_results(db_controller: DBController, user_id: int) \
        -> list[tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]:
    return db_controller.get_all_unit_economy_results(user_id)


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
}


def __delete_unit_economy_request(db_controller: DBController, request_id: int, user_id: int):
    db_controller.delete_unit_economy_request_for_user(request_id, user_id)


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
}

T = TypeVar('T')


class RequestHandler:
    def __init__(self, db_controller: DBController,
                 save_methods: dict[Type[JBasicSaveObject],
                 Callable[
                     [
                         DBController,
                         JBasicSaveObject | JEconomySaveObject,
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
        return self.__save_request_by_method(save_method, self.__db_controller, save_object, user_id)

    @staticmethod
    def __save_request_by_method(save_method: Callable[[DBController, JBasicSaveObject, int, bool], int],
                                 db_controller: DBController, save_object: JBasicSaveObject, user_id: int) -> int:
        try:
            return save_method(db_controller, save_object, user_id, False)
        except Exception:
            print("SAVED TO DEFAULT CATEGORY")
            return save_method(db_controller, save_object, user_id, True)

    def get_all_request_results(self, user_id: int, request_type: Type[JBasicSaveObject]) \
            -> list[tuple[Request, Result, RequestInfo]]:
        get_all_method = self.__get_executed_method(request_type, self.__GET_ALL_METHODS)
        return get_all_method(self.__db_controller, user_id)

    def delete_request(self, request_id: int, user_id: int, request_type: Type[JBasicSaveObject]) -> None:
        delete_method = self.__get_executed_method(request_type, self.__DELETE_METHODS)
        delete_method(self.__db_controller, request_id, user_id)
