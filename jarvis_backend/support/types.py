from jorm.market.service import UnitEconomyRequest, UnitEconomyResult, Request, Result, RequestInfo


class JBasicSaveObject:
    request_type = Request
    result_type = Result
    info: RequestInfo

    def __init__(self, request: Request, result: Result, info: RequestInfo):
        self.request = request
        self.result = result
        self.info: RequestInfo = info


class JEconomySaveObject(JBasicSaveObject):
    request_type = UnitEconomyRequest
    result_type = UnitEconomyResult

    def __init__(self, request: UnitEconomyRequest, result: UnitEconomyResult, info: RequestInfo):
        super().__init__(request, result, info)
