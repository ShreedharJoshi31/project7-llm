# app/services/groq_service.py

import json
import os
from groq import Groq

client = Groq(api_key="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")

async def stream_groq_response(prompt: str, websocket):
    # Stream response from Groq
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Provide output in markdown."},
            {"role": "user", "content": prompt},
        ],
        model="llama3-8b-8192",
        stream=True,
    )

    # Stream each chunk of the response to the WebSocket
    for chunk in stream:
        # delta_content = chunk.choices[0].delta.get("content", "")
        # if delta_content:
            # await websocket.send_json({"response": delta_content})
        await websocket.send_json({"response": chunk.choices[0].delta.content})
