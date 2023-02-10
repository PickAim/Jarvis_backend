import time

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from app.routers import routers
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

for router in routers:
    app.include_router(router)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    return await call_next(request)

@app.post("/delete_all_cookie/")
def delete_cookie():
    response = JSONResponse(content="deleted")
    return CookieHandler.delete_all_cookie(response)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
