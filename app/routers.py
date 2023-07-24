from fastapi import APIRouter

from app.auth_api import SessionAPI
from app.calc.economy_analyze_api import EconomyAnalyzeAPI
from app.calc.niche_analyze_api import NicheFrequencyAPI, NicheCharacteristicsAPI
from app.calc.product_analyze_api import ProductDownturnAPI, ProductTurnoverAPI
from app.info_api import InfoAPI
from app.tokens.token_api import TokenAPI

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
