import argparse
import asyncio
import websockets
import aiohttp
import json
import os
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from get_embedding_function import get_embedding_function
from groq import Groq

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

# Create Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Function to stream response from Groq API and send it via WebSocket
async def stream_groq_response(prompt: str, websocket):
    # Stream response from Groq
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stream=True,  # Enable streaming
    )

    # Stream each chunk of the response to the WebSocket
    for chunk in stream:
        delta_content = chunk.choices[0].delta.get("content", "")
        if delta_content:
            await websocket.send(json.dumps({"response": delta_content}))

async def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    return prompt, results

async def websocket_handler(websocket, path):
    async for message in websocket:
        # Expecting the message to be a JSON object with a "query" key
        try:
            data = json.loads(message)
            query_text = data.get("query", "").strip()

            if not query_text:
                await websocket.send(json.dumps({"error": "No query provided"}))
                continue

            prompt, results = await query_rag(query_text)

            # Stream response from Groq and send it via WebSocket
            await stream_groq_response(prompt, websocket)

        except json.JSONDecodeError:
            await websocket.send(json.dumps({"error": "Invalid JSON format"}))

async def main():
    async with websockets.serve(websocket_handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    # Start WebSocket server
    asyncio.run(main())
