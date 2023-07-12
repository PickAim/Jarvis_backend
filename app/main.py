import logging
from os import path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from app.loggers import ERROR_LOGGER
from app.routers import routers
from sessions.controllers import CookieHandler
from sessions.exceptions import JARVIS_EXCEPTION_KEY

app = FastAPI()

origins = [
    # "http://localhost",  # temp
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)


@app.post("/delete_all_cookie/")
def delete_cookie():
    response = JSONResponse(content="deleted")
    return CookieHandler.delete_all_cookie(response)


@app.exception_handler(Exception)
async def exception_handler(_, exc):
    logger = logging.getLogger(ERROR_LOGGER)
    logger.exception("Unhandled exception", stacklevel=5, exc_info=True)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc):
    if JARVIS_EXCEPTION_KEY not in exc.detail:
        logger = logging.getLogger(ERROR_LOGGER)
        logger.exception("Unhandled http exception", stacklevel=5, exc_info=True)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


if __name__ == '__main__':
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.ini')
    uvicorn.run(app=app, port=8090, log_config=log_file_path)
