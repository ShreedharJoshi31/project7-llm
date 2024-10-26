# app/utils/rag_utils.py

from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from app.utils.get_embedding_function import get_embedding_function
from app.utils.prompts import PROMPT_TEMPLATE

CHROMA_PATH = "chroma"

async def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    return prompt, results
