from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from brotli_asgi import BrotliMiddleware
import orjson


from api.core.exception_handlers import (
    http_exception,
    redis_exception_handler,
    sqlalchemy_exception_handler,
    exception,
    validation_excption_handler,
)
from api.core.middleware import RequestLoggerMiddleware, SetHeadersMiddleware
from starlette.middleware.sessions import SessionMiddleware
from api.database.database import async_engine
from api.utils.task_logger import create_logger
from api.v1 import api_version_one
from api.v1.seed.seed import seed_users
from api.utils.settings import Config

logger = create_logger("Main App")


def orjson_dumps(v, *, default):
    """
    Custom JSON response class using orjson to serialize payloads.
    """
    return orjson.dumps(v, default=default).decode()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App instance lifspan
    """
    await seed_users()
    logger.info(msg="Starting Application")
    try:
        yield
    finally:
        await async_engine.dispose()
        logger.info(msg="Shutting Down Application")


app = FastAPI(
    title="Freeman FastAPI Boilerplate",
    description="Freeman FastAPI Boilerplate documentation",
    version="1.0.0",
    lifespan=lifespan,
    json_dumps=orjson_dumps,
    json_loads=orjson_dumps,
)


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods="*",
    allow_headers="*",
)


app.add_middleware(
    BrotliMiddleware, minimum_size=500
)  # compress response larger than 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(SetHeadersMiddleware)
app.add_middleware(SessionMiddleware, secret_key=Config.SECRET_KEY)

app.include_router(api_version_one)


@app.get("/", tags=["HOME"])
async def read_root() -> dict:
    """
    Read root
    """
    return {"message": "Welcome to Freeman FastAPI Boilerplate"}


app.add_exception_handler(HTTPException, http_exception)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(RequestValidationError, validation_excption_handler)
app.add_exception_handler(RedisError, redis_exception_handler)
app.add_exception_handler(Exception, exception)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=7001,
        host="0.0.0.0/0",
        reload=True,
        timeout_keep_alive=60,
    )
