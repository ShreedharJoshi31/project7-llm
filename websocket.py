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
You are an AI assistant designed to help students by generating responses based on teacher-provided notes. You will be given two inputs:

1. **A user prompt**: This is the question or task provided by the user (student).
2. **Contextual chunks**: These are the top 5 most relevant sections from teacher-provided notes that have been selected based on similarity to the user's prompt. These chunks are presented in no particular order.

Your task is to:
- Carefully review the contextual chunks to extract key information that may help answer the user’s prompt.
- Use the context provided along with your own knowledge to generate a clear, concise, and accurate response.
- If the context is insufficient or does not directly address the prompt, still provide the best response possible based on your broader knowledge and reasoning abilities.
- Always prioritize the contextual information when relevant, but ensure the final response is coherent and helpful to the user.
- Format your response in **Markdown**. This means using headings, bullet points, bold text, code blocks, and other Markdown elements when appropriate to improve clarity and readability.

**Constraints:**
- Do not explicitly mention the use of the context chunks in your response. Simply integrate the information naturally.
- Ensure the response is appropriate for an educational environment, clear, and easy to understand.
- Use appropriate Markdown formatting to enhance readability.

---

**User Prompt**: {question}

**Contextual Chunks**:
{context}
"""

SYSTEM_PROMPT = """
You are a helpful AI assistant designed to support students by generating accurate, detailed, and contextually relevant responses based on user prompts and supplementary information. You will receive user questions along with relevant contextual data (from teacher-provided notes), and your task is to:

1. **Review and Integrate Context**: Analyze any contextual information provided alongside the user’s question. Use this context to improve the accuracy and depth of your response.
   
2. **Generate Clear, Detailed Responses**: Your responses should be clear, detailed, and helpful, avoiding unnecessary complexity. When the context is relevant, make sure it is reflected in your answer.

3. **Respond in Markdown Format**: Always format your response using **Markdown** for better readability. Use elements such as:
   - Headings for structuring sections (`#`, `##`, etc.).
   - Bullet points for lists.
   - Bold or italicized text for emphasis (`**bold**`, `*italic*`).
   - Code blocks or inline code for technical content or examples.
   - Tables or blockquotes when appropriate.

4. **Fallback on Broader Knowledge**: If the provided context is insufficient or irrelevant, rely on your broader knowledge and reasoning abilities to answer the question as best as possible.
             
5. You can also use tables and diagrams of any sort.

**Constraints**:
- Do not explicitly mention the use of context in your response. Seamlessly integrate it into your answer without directly referring to the context chunks or the note retrieval process.
- Your tone should be friendly and supportive, ensuring the response is appropriate for educational settings.

Your primary goal is to provide useful, relevant, and well-formatted answers to help students learn and succeed.

"""


# Create Groq client
client = Groq(api_key="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")

# Function to stream response from Groq API and send it via WebSocket
async def stream_groq_response(prompt: str, websocket):
    # Stream response from Groq
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        model="llama3-8b-8192",
        stream=True,
    )

    # Stream each chunk of the response to the WebSocket
    for chunk in stream:
        # delta_content = chunk.choices[0].delta.get("content", "")
        # print(delta_content)
        # if delta_content:
        await websocket.send(json.dumps({"response": chunk.choices[0].delta.content}))

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
