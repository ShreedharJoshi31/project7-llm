import asyncio
import json
from fastapi import FastAPI
from fastapi import WebSocket, WebSocketDisconnect
import uvicorn
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from groq import Groq
from endpoints import router  # Import the router from endpoints.py

CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Answer the question using the following context if necessary:

{context}

---

Answer the question based on the above context: {question}
"""

# Create Groq client
client = Groq(api_key="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")

# Initialize FastAPI app
app = FastAPI()
app.include_router(router)  # Include the router from endpoints.py


# Helper function to prepare a RAG query
async def query_rag(query_text: str):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    return prompt, results


# Helper function to stream response from Groq API via WebSocket
async def stream_groq_response(prompt: str, websocket: WebSocket):
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant give the outputs in markdown."},
            {"role": "user", "content": prompt},
        ],
        model="llama3-8b-8192",
        stream=True,
    )

    for chunk in stream:
        try:
            content = chunk.choices[0].delta.get("content", "")
            if content:
                await websocket.send_json({"response": content})
        except WebSocketDisconnect:
            print("WebSocket disconnected.")
            break


if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn
    uvicorn.run("websocket:app", host="0.0.0.0", port=8765, reload=True)