from jorm.market.service import FrequencyRequest, FrequencyResult, UnitEconomyRequest, UnitEconomyResult, Request, \
    Result, RequestInfo


class JBasicSaveObject:
    request_type = Request
    result_type = Result
    info: RequestInfo

    def __init__(self, request: Request, result: Result, info: RequestInfo):
        self.request = request
        self.result = result
        self.info: RequestInfo = info


class JFrequencySaveObject(JBasicSaveObject):
    request_type = FrequencyRequest
    result_type = FrequencyResult

    def __init__(self, request: FrequencyRequest, result: FrequencyResult, info: RequestInfo):
        super().__init__(request, result, info)


class JEconomySaveObject(JBasicSaveObject):
    request_type = UnitEconomyRequest
    result_type = UnitEconomyResult

    def __init__(self, request: UnitEconomyRequest, result: UnitEconomyResult, info: RequestInfo):
        super().__init__(request, result, info)
