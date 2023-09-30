import asyncio
import json
import logging
import time
from os import path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jarvis_factory.factories.jdb import JDBClassesFactory
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.jarvis.db_update import JORMChanger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from jarvis_backend.app.loggers import ERROR_LOGGER
from jarvis_backend.app.routers import routers
from jarvis_backend.app.tags import tags_metadata, OTHER_TAG
from jarvis_backend.controllers.cookie import CookieHandler
from jarvis_backend.sessions.dependencies import db_context_depends, init_defaults
from jarvis_backend.sessions.exceptions import JARVIS_EXCEPTION_KEY, JARVIS_DESCRIPTION_KEY, JarvisExceptionsCode, \
    JarvisExceptions

app = FastAPI(openapi_tags=tags_metadata)

REQUEST_TIMEOUT_ERROR = 300

origins = [
    "http://localhost:8300"
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


def load_niche(jorm_changer: JORMChanger, niche_name: str, marketplace_id: int):
    return jorm_changer.load_new_niche(niche_name, marketplace_id)


def update_niche(jorm_changer: JORMChanger, niche_id: int, category_id: int, marketplace_id: int):
    return jorm_changer.update_niche(niche_id, category_id, marketplace_id)


def main_load():
    niche_to_category: dict[str, str] = {}
    db_context = db_context_depends()
    with db_context.session() as session, session.begin():
        init_defaults(session)
    with open('../commission.csv', "r", encoding='cp1251') as file:
        lines: list[str] = file.readlines()
        print()
        print(f'# | Niche name | status | length')
        skip = 133
        step = 10
        for i in range(skip, len(lines), step):
            splitted: list[str] = lines[i].split(";")
            niche_to_category[splitted[1]] = splitted[0]
            with db_context.session() as session, session.begin():
                jorm_changer = JDBClassesFactory.create_jorm_changer(session, marketplace_id=2, user_id=0)
                try:
                    print(f"loading {splitted[1]}")
                    niche = load_niche(jorm_changer, splitted[1], 2)
                    print(f'{i} | {niche.name}| loaded | {len(niche.products)}')
                except Exception as ex:
                    print(f'{i} | {splitted[1]}| NOT LOADED | ----- {ex}')


def main_update():
    db_context = db_context_depends()
    marketplace_id = 2
    with db_context.session() as session, session.begin():
        category_service = JDBServiceFactory.create_category_service(session)
        id_to_category = category_service.find_all_in_marketplace(marketplace_id)
    category_to_niche = {}
    with db_context.session() as session, session.begin():
        niche_service = JDBServiceFactory.create_niche_service(session)
        for category_id in id_to_category:
            category_to_niche[category_id] = list(niche_service.find_all_in_category(category_id).keys())
    start_from = -1
    for category_id in category_to_niche:
        for niche_id in category_to_niche[category_id]:
            if niche_id >= start_from:
                with db_context.session() as session, session.begin():
                    try:
                        jorm_changer = JDBClassesFactory.create_jorm_changer(session, marketplace_id, user_id=0)
                        update_niche(jorm_changer, niche_id, category_id, marketplace_id)
                        print(f"niche #{niche_id} updated")
                    except Exception as ex:
                        print(f"niche #{niche_id} NOT updated, cause: {str(ex)}")


def main_start():
    db_context = db_context_depends()
    with db_context.session() as session, session.begin():
        init_defaults(session)
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.ini')
    uvicorn.run(app=app, port=8090, log_config=log_file_path)


if __name__ == '__main__':
    main_start()
