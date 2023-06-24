from jorm.market.service import FrequencyRequest, FrequencyResult, UnitEconomyRequest, UnitEconomyResult

from sessions.request_items import RequestInfo


class JBasicSaveObject:
    info: RequestInfo

    def __init__(self, info: RequestInfo):
        self.info: RequestInfo = info


class JFrequencySaveObject(JBasicSaveObject):
    def __init__(self, request: FrequencyRequest, result: FrequencyResult, info: RequestInfo):
        super().__init__(info)
        self.request: FrequencyRequest = request
        self.result: FrequencyResult = result


class JEconomySaveObject(JBasicSaveObject):
    def __init__(self, request: UnitEconomyRequest, result: UnitEconomyResult, info: RequestInfo):
        super().__init__(info)
        self.request: UnitEconomyRequest = request
        self.result: UnitEconomyResult = result
