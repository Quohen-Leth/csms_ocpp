import logging

import uvicorn
from fastapi import FastAPI

from src.api.routers import http_router
from src.settings import settings
from src.csms.routers import websocket_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.include_router(http_router)
app.include_router(websocket_router)


if __name__ == "__main__":
    uvicorn.run("src.__main__:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
