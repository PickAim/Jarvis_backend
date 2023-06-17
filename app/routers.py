from fastapi import APIRouter

from app.calc.economy_analyze_requests import EconomyAnalyzeAPI
from app.calc.niche_analyze_requests import NicheFrequencyAPI
from app.calc.product_analyze_requests import ProductDownturnAPI
from app.session_requests import SessionAPI
from app.tokens.requests import TokenAPI

routers: list[APIRouter] = [
    TokenAPI.router,
    SessionAPI.router,
    NicheFrequencyAPI.router,
    EconomyAnalyzeAPI.router,
    ProductDownturnAPI.router
]
