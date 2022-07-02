from fastapi import APIRouter

from src.api import schemas
from src.csms.central_system_handler import central_system

http_router = APIRouter()


@http_router.get("/")
async def view_chargers():
    response = await central_system.view_chargers()
    return {"Connected Charging Stations": response}


@http_router.post("/base-report")
async def get_base_report(data: schemas.MinModel):
    return await central_system.get_base_report(data.cp_id)


@http_router.post("/start-transaction")
async def start_transaction(data: schemas.MinModel):
    return await central_system.start_transaction(data.cp_id)


@http_router.post("/stop-transaction")
async def stop_transaction(data: schemas.MinModel):
    return await central_system.stop_transaction(data.cp_id)