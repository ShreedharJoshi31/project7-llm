# app/routers/websocket.py

from fastapi import APIRouter, WebSocket

from app.controllers.websocket_controller import websocket_handler

router = APIRouter()

@router.websocket("/generate")
async def websocket_route(websocket: WebSocket):
    await websocket_handler(websocket)
