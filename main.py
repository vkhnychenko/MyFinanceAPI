from asyncio import sleep

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from database import database, metadata, engine
from settings import settings
from auth.api import auth_router
from bot.api import bot_router
from bot.services import get_new_transactions

app = FastAPI()


metadata.create_all(engine)
app.state.database = database

app.include_router(auth_router)
app.include_router(bot_router)

templates = Jinja2Templates(directory="templates")


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.websocket("/ws/transactions")
async def ws_new_transactions(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await get_new_transactions()
        for obj in data:
            await websocket.send_text(obj.json())
        await sleep(5)


if __name__ == '__main__':
    uvicorn.run("main:app", host=settings.server_host, port=settings.server_port)
