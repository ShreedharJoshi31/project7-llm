# app/routers/websocket.py

from fastapi import APIRouter, WebSocket

from app.controllers.generate_controller import generate_handler

router = APIRouter()

@router.websocket("/generate")
async def generate_route(websocket: WebSocket):
    await generate_handler(websocket)
