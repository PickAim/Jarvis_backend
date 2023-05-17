import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from app.calc.product_analyze_requests import product_analyze_router
from app.session_requests import session_router
from app.tokens.requests import token_router
from calc.economy_analyze_requests import unit_economy_router
from sessions.controllers import CookieHandler

app = FastAPI()

origins = [
    # "http://localhost", # temp
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(token_router)
app.include_router(session_router)
app.include_router(unit_economy_router)
app.include_router(product_analyze_router)
app.include_router(unit_economy_router)


@app.post("/delete_all_cookie/")
def delete_cookie():
    response = JSONResponse(content="deleted")
    return CookieHandler.delete_all_cookie(response)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
