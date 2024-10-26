# app/controllers/websocket_controller.py

import json
from fastapi import WebSocket
from app.utils.rag_utils import query_rag
from app.services.groq_service import stream_groq_response

async def generate_handler(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message in websocket.iter_text():
            try:
                data = json.loads(message)
                query_text = data.get("query", "").strip()

                if not query_text:
                    await websocket.send_json({"error": "No query provided"})
                    continue

                # Get the prompt and RAG results
                prompt, _ = await query_rag(query_text)

                # Stream response from Groq and send it via WebSocket
                await stream_groq_response(prompt, websocket)

            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
    except Exception as e:
        print(f"Connection closed with error: {e}")
    finally:
        await websocket.close()
