import asyncio
import json
import logging
import time
from os import path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from jarvis_backend.app.loggers import ERROR_LOGGER
from jarvis_backend.app.routers import routers
from jarvis_backend.app.tags import tags_metadata, OTHER_TAG
from jarvis_backend.sessions.controllers import CookieHandler
from jarvis_backend.sessions.dependencies import init_defaults, db_context_depends
from jarvis_backend.sessions.exceptions import JARVIS_EXCEPTION_KEY, JARVIS_DESCRIPTION_KEY, JarvisExceptionsCode, \
    JarvisExceptions

app = FastAPI(openapi_tags=tags_metadata)

REQUEST_TIMEOUT_ERROR = 300

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


@app.middleware("http")
@app.middleware("https")
async def timeout_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT_ERROR)
    except asyncio.TimeoutError:
        process_time = time.time() - start_time
        raise JarvisExceptions.create_exception_with_code(
            JarvisExceptionsCode.TIMEOUT,
            f"Request processing time exceed limit({REQUEST_TIMEOUT_ERROR})."
            f"Processing time: {process_time}"
        )


@app.post("/delete_all_cookie/", tags=[OTHER_TAG])
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
    logger = logging.getLogger(ERROR_LOGGER)
    if JARVIS_EXCEPTION_KEY not in exc.detail:
        logger.exception("Unhandled http exception", stacklevel=5, exc_info=True)
    else:
        parsed_details = json.loads(exc.detail)
        logger.warning(f"Jarvis handled warning - "
                       f"{parsed_details[JARVIS_EXCEPTION_KEY]}: "
                       f"{parsed_details[JARVIS_DESCRIPTION_KEY]}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


if __name__ == '__main__':
    db_context = db_context_depends()
    with db_context.session() as session, session.begin():
        init_defaults(session)
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.ini')
    uvicorn.run(app=app, port=8090, log_config=log_file_path)
