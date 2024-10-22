import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from websocket import query_rag, stream_groq_response  # Import helper functions

# Create a router to hold the endpoints
router = APIRouter()

# WebSocket route for handling RAG-based queries
@router.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            query_text = data.get("query", "").strip()

            if not query_text:
                await websocket.send_json({"error": "No query provided"})
                continue

            prompt, results = await query_rag(query_text)
            await stream_groq_response(prompt, websocket)

    except WebSocketDisconnect:
        print("WebSocket connection closed.")


# WebSocket route for simple echo (for testing)
@router.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Echo WebSocket disconnected.")


# HTTP route for health check
@router.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})