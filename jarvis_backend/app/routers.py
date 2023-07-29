from fastapi import APIRouter

from jarvis_backend.app.auth_api import SessionAPI
from jarvis_backend.app.calc.economy_analyze_api import EconomyAnalyzeAPI
from jarvis_backend.app.calc.niche_analyze_api import NicheFrequencyAPI, NicheCharacteristicsAPI
from jarvis_backend.app.calc.product_analyze_api import ProductDownturnAPI, ProductTurnoverAPI
from jarvis_backend.app.info_api import InfoAPI
from jarvis_backend.app.tokens.token_api import TokenAPI

routers: list[APIRouter] = [
    TokenAPI.router,
    SessionAPI.router,
    NicheFrequencyAPI.router,
    EconomyAnalyzeAPI.router,
    ProductDownturnAPI.router,
    ProductTurnoverAPI.router,
    NicheCharacteristicsAPI.router,
    InfoAPI.router
]
