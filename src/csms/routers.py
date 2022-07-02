import logging

from fastapi import APIRouter, WebSocket

from src.settings import settings
from src.csms.central_system_handler import central_system
from src.csms.charge_point_handler import ChargePointHandler

websocket_router = APIRouter()


class SocketAdapter:
    """ Adapter between FastAPI WebSocket and websockets lib."""
    def __init__(self, websocket: WebSocket):
        self._ws = websocket

    async def recv(self):
        return await self._ws.receive_text()

    async def send(self, msg):
        await self._ws.send_text(msg)


@websocket_router.websocket("/{station_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        station_id: str,
):
    await websocket.accept(subprotocol=settings.WEBSOCKETS_SUBPROTOCOL)
    charge_point = ChargePointHandler(station_id, SocketAdapter(websocket))
    logging.info(f"Charging station {charge_point.id} connected.")
    queue = central_system.register_charger(charge_point)
    await queue.get()
