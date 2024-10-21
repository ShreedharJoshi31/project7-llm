import argparse
import asyncio
import websockets
import aiohttp
import json
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

async def fetch_streamed_response(prompt: str, session: aiohttp.ClientSession):
    url = "https://fast-api.snova.ai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer c2hyZWVkaGFyam9zaGkwM0BnbWFpbC5jb206bnVxY1J6NHl4aTRZUU5feA==",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": "Answer the question in detail."},
            {"role": "user", "content": prompt}
        ],
        "stop": ["[INST", "[INST]", "[/INST]", "[/INST]"],
        "model": "Meta-Llama-3.1-8B-Instruct",
        "stream": True,
        "stream_options": {"include_usage": True}
    }

    async with session.post(url, json=payload, headers=headers) as response:
        async for line in response.content:
            yield line

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
    async with aiohttp.ClientSession() as session:
        async for message in websocket:
            # Expecting the message to be a JSON object with a "query" key
            try:
                data = json.loads(message)
                query_text = data.get("query", "").strip()

                if not query_text:
                    await websocket.send(json.dumps({"error": "No query provided"}))
                    continue

                prompt, results = await query_rag(query_text)

                async for response in fetch_streamed_response(prompt, session):
                    await websocket.send(response.decode('utf-8'))

                print("HO GAYA")

            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON format"}))
                print("Nahi hua")

async def main():
    async with websockets.serve(websocket_handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    # Create CLI if needed for other purposes
    # parser = argparse.ArgumentParser()
    # parser.add_argument("query_text", type=str, help="The query text.")
    # args = parser.parse_args()

    # Start WebSocket server
    asyncio.run(main())
