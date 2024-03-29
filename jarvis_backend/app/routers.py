from fastapi import APIRouter

from jarvis_backend.app.auth_api import SessionAPI
from jarvis_backend.app.calc.economy_analyze_api import SimpleEconomyAnalyzeAPI, TransitEconomyAnalyzeAPI
from jarvis_backend.app.calc.niche_analyze_api import NicheCharacteristicsAPI, GreenTradeZoneAPI
from jarvis_backend.app.calc.product_analyze_api import ProductDownturnAPI, ProductTurnoverAPI, AllProductCalculateAPI, \
    NearestKeywordsForProductAPI, NearestKeywordsAPI
from jarvis_backend.app.info_api import InfoAPI
from jarvis_backend.app.tokens.token_api import TokenAPI
from jarvis_backend.app.user_api import UserAPI

routers: list[APIRouter] = [
    TokenAPI.router,
    SessionAPI.router,
    SimpleEconomyAnalyzeAPI.router,
    TransitEconomyAnalyzeAPI.router,
    ProductDownturnAPI.router,
    ProductTurnoverAPI.router,
    NicheCharacteristicsAPI.router,
    GreenTradeZoneAPI.router,
    AllProductCalculateAPI.router,
    NearestKeywordsAPI.router,
    NearestKeywordsForProductAPI.router,
    InfoAPI.router,
    UserAPI.router
]
